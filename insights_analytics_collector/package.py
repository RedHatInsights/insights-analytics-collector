from abc import abstractmethod
import base64
import io
import json
import os
import pathlib
import requests
import tarfile


class Package:
    """
    Abstract class
    Package serves for managing one tarball and shipping it to the cloud.
    Abstract methods has to be implemented, as well as:
    - CERT_PATH - path to auth certificate (for POST request to cloud), if not development mode
    - PAYLOAD_CONTENT_TYPE - registered in ingress-service in cloud
    - MAX_DATA_SIZE - defaults to 200MB (upload limit is 100MB, so it expects 50% compression rate)
    """

    CERT_PATH = "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem"
    PAYLOAD_CONTENT_TYPE = "application/vnd.redhat.TODO+tgz"  # i.e. "application/vnd.redhat.tower.tower_payload+tgz"

    SHIPPING_AUTH_USERPASS = 'user-pass'
    SHIPPING_AUTH_IDENTITY = 'x-rh-identity'  # Development mode only

    '''
    Some tables can be *very* large, and we have a 100MB upload limit.

    Split large table dumps at dump time into a series of files.
    '''
    MAX_DATA_SIZE = 200 * 1048576

    def __init__(self, collector):
        self.collector = collector
        self.collections = []
        self.collection_keys = []
        self.logger = collector.logger
        self.manifest = {}
        self.processed = False
        self.shipping_successful = None
        self.tar_path = None
        self.total_data_size = 0

    @classmethod
    def max_data_size(cls):
        return cls.MAX_DATA_SIZE

    def add_collection(self, collection):
        self.collections.append(collection)
        self.collection_keys.append(collection.key)
        self.total_data_size = self.total_data_size + collection.data_size()

    def is_key_used(self, key):
        return key in self.collection_keys

    def delete_collected_files(self):
        for collection in self.collections:
            collection.cleanup()

    @abstractmethod
    def get_ingress_url(self):
        """URL of cloud's upload URL"""
        pass

    def has_free_space(self, requested_size):
        return self.total_data_size + requested_size <= self.max_data_size()

    def is_shipping_configured(self):
        if not self.tar_path:
            self.logger.error('Insights for Ansible Automation Platform TAR not found')
            return False

        if not os.path.exists(self.tar_path):
            self.logger.error(f'Insights for Ansible Automation Platform TAR {self.tar_path} not found')
            return False

        if "Error:" in str(self.tar_path):
            return False

        if not self.get_ingress_url():
            self.logger.error('AUTOMATION_ANALYTICS_URL is not set')
            return False

        if self.shipping_auth_mode() == self.SHIPPING_AUTH_USERPASS:
            if not self._get_rh_user():
                self.logger.error('REDHAT_USERNAME is not set')
                return False

            if not self._get_rh_password():
                self.logger.error('REDHAT_PASSWORD is not set')
                return False

        return True

    def make_tgz(self):
        target = self.collector.tmp_dir.parent
        try:
            tarname_base = self._tarname_base()
            path = pathlib.Path(target)
            index = len(list(path.glob(f'{tarname_base}-*.*')))
            tarname = f'{tarname_base}-{index}.tar.gz'

            with tarfile.open(target.joinpath(tarname), 'w:gz') as f:
                for collection in self.collections:
                    self._collection_to_tar(f, collection)

                self._config_to_tar(f)
                self._manifest_to_tar(f)
                # TODO
                # self._data_collection_status_to_tar(f)

                self.tar_path = f.name
            return True
        except Exception as e:
            self.logger.exception(f"Failed to write analytics archive file: {e}")
            return False

    def ship(self):
        """
        Ship gathered metrics to the Insights API
        """
        if not self.is_shipping_configured():
            self.shipping_successful = False
            return False

        self.logger.debug(f'shipping analytics file: {self.tar_path}')

        with open(self.tar_path, 'rb') as f:
            files = {'file': (os.path.basename(self.tar_path), f, self._payload_content_type())}
            s = requests.Session()
            s.headers = self._get_http_request_headers()
            s.headers.pop('Content-Type')

            if self.shipping_auth_mode() == self.SHIPPING_AUTH_IDENTITY:
                s.headers['x-rh-identity'] = self._get_x_rh_identity()

            url = self.get_ingress_url()
            self.shipping_successful = self._send_data(url, files, s)

        return self.shipping_successful

    def shipping_auth_mode(self):
        return self.SHIPPING_AUTH_USERPASS

    def update_last_gathered_entries(self, updates_dict):
        if self.shipping_successful:
            for collection in self.collections:
                collection.update_last_gathered_entries(updates_dict)

    #
    # Private methods ---------------------------
    #

    def _collection_to_tar(self, tar, collection):
        try:
            if not collection.is_empty():
                collection.add_to_tar(tar)
                self._update_manifest(collection)
        except Exception as e:
            self.logger.exception(f"Could not generate metric {collection.filename}: {e}")
            return None

    def _send_data(self, url, files, session):
        if self.shipping_auth_mode() == self.SHIPPING_AUTH_USERPASS:
            response = session.post(
                url, files=files, verify=self.CERT_PATH,
                auth=(self._get_rh_user(), self._get_rh_password()), headers=session.headers, timeout=(31, 31)
            )
        else:
            response = session.post(
                url, files=files, headers=session.headers, timeout=(31, 31)
            )

        # Accept 2XX status_codes
        if response.status_code >= 300:
            self.logger.error('Upload failed with status {}, {}'.format(response.status_code, response.text))
            return False

        return True

    def _config_to_tar(self, tar):
        if self.collector.collections['config'] is None:
            self.logger.error("'config' collector data is missing, and is required to ship.")
            return False
        else:
            self._collection_to_tar(tar, self.collector.collections['config'])

        return True

    @abstractmethod
    def _get_http_request_headers(self):
        """Optional HTTP headers for POST request to get_ingress_url() URL
        :return: dict()
        """
        pass

    @abstractmethod
    def _get_rh_user(self):
        """Auth: username for HTTP POST request to cloud.
                 shipping_auth_mode() must return SHIPPING_AUTH_USERPASS (default)
        """
        pass

    @abstractmethod
    def _get_rh_password(self):
        """Auth: password for HTTP POST request to cloud.
                 shipping_auth_mode() must return SHIPPING_AUTH_USERPASS (default)
        """

        pass

    def _get_x_rh_identity(self):
        """Auth: x-rh-identity header for HTTP POST request to cloud
        Optional, if shipping_auth_mode() redefined to SHIPPING_AUTH_IDENTITY
        """
        identity = {"identity": {"type": "User", "account_number": "0000001", "user": {"is_org_admin": True},
                                 "internal": {"org_id": "000001"}}}
        identity = base64.b64encode(json.dumps(identity).encode('utf8'))
        return identity

    # TODO: duplicate with CollectionJSON's code
    def _manifest_to_tar(self, tar):
        try:
            buf = json.dumps(self.manifest).encode('utf-8')
            info = tarfile.TarInfo('./manifest.json')
            info.size = len(buf)
            info.mtime = self.collector.gather_until.timestamp()
            tar.addfile(info, fileobj=io.BytesIO(buf))
        except Exception as e:
            self.logger.exception(f"Could not generate manifest.json: {e}")
            return None

    def _payload_content_type(self):
        return self.PAYLOAD_CONTENT_TYPE

    def _update_manifest(self, collection):
        self.manifest[collection.filename] = collection.version

    def _tarname_base(self):
        timestamp = self.collector.gather_until
        return f'analytics-{timestamp.strftime("%Y-%m-%d-%H%M%S%z")}'
