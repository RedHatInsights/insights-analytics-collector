from tests.classes.analytics_collector import AnalyticsCollector
import tests.functional.collector_module
import tests.functional.collector_module2
import json
import logging
import pytest
import tarfile


@pytest.fixture
def collector(mocker):
    collector = AnalyticsCollector(collector_module=tests.functional.collector_module,
                                   collection_type=AnalyticsCollector.DRY_RUN)
    mocker.patch.object(collector, '_is_valid_license', return_value=True)

    return collector


def test_missing_config(mocker, collector):
    mock_logger = mocker.patch.object(collector, 'logger')

    tgz_files = collector.gather(subset=['json_collection_1', 'json_collection_2'])

    assert tgz_files is None
    mock_logger.log.assert_called_with(logging.ERROR, "'config' collector data is missing")


def test_json_collections(collector):
    tgz_files = collector.gather(subset=['config', 'json_collection_1', 'json_collection_2'])

    assert len(tgz_files) == 1

    files = {}
    with tarfile.open(tgz_files[0], "r:gz") as archive:
        for member in archive.getmembers():
            files[member.name] = archive.extractfile(member)

        _assert_common_files(files)
        assert './json_collection_1.json' in files.keys()
        assert './json_collection_2.json' in files.keys()

        assert json.loads(files['./config.json'].read()) == {'version': '1.0'}
        assert json.loads(files['./json_collection_1.json'].read()) == {'json1': 'True'}
        assert json.loads(files['./json_collection_2.json'].read()) == {'json2': 'True'}

    collector._gather_cleanup()


def test_small_csvs(collector):
    tgz_files = collector.gather(subset=['config', 'csv_collection_1', 'csv_collection_2', 'csv_collection_3'])

    assert len(tgz_files) == 1

    files = {}
    with tarfile.open(tgz_files[0], "r:gz") as archive:
        for member in archive.getmembers():
            files[member.name] = archive.extractfile(member)

        _assert_common_files(files)
        assert './csv_collection_1.csv' in files.keys()
        assert './csv_collection_2.csv' in files.keys()
        assert './csv_collection_3.csv' in files.keys()

        # length defined by @registered function
        assert len(files['./csv_collection_1.csv'].read()) == 100
        assert len(files['./csv_collection_2.csv'].read()) == 200
        assert len(files['./csv_collection_3.csv'].read()) == 300

    collector._gather_cleanup()


def test_one_csv_collection_splitted_by_size(collector):
    tgz_files = collector.gather(subset=['config', 'big_table'])

    assert(len(tgz_files) == 10)

    for i in range(len(tgz_files)):
        files = {}
        with tarfile.open(tgz_files[i], "r:gz") as archive:
            for member in archive.getmembers():
                files[member.name] = archive.extractfile(member)

            _assert_common_files(files)
            assert len(files.keys()) == 1 + _common_files_count()
            assert './big_table.csv' in files.keys()
            assert len(files['./big_table.csv'].read()) == 1000

    collector._gather_cleanup()


def test_multiple_collections_multiple_tarballs(mocker, collector):
    mocker.patch('tests.classes.package.Package.MAX_DATA_SIZE', 1000)

    tgz_files = collector.gather(subset=['config', 'big_table_2', 'csv_collection_1', 'csv_collection_2'])

    assert(len(tgz_files) == 3)

    for i in range(len(tgz_files)):
        files = {}
        with tarfile.open(tgz_files[i], "r:gz") as archive:
            for member in archive.getmembers():
                files[member.name] = archive.extractfile(member)

            _assert_common_files(files)
            if i == 0:
                assert len(files.keys()) == 2 + _common_files_count()
                assert './big_table_2.csv' in files.keys()
                assert './csv_collection_1.csv' in files.keys()
            elif i == 1:
                assert len(files.keys()) == 2 + _common_files_count()
                assert './big_table_2.csv' in files.keys()
                assert './csv_collection_2.csv' in files.keys()
            elif i == 2:
                assert len(files.keys()) == 1 + _common_files_count()
                assert './big_table_2.csv' in files.keys()

    collector._gather_cleanup()


def test_manifest(collector):
    collector.collector_module = tests.functional.collector_module2
    tgz_files = collector.gather()

    assert len(tgz_files) == 1

    files = {}
    with tarfile.open(tgz_files[0], "r:gz") as archive:
        for member in archive.getmembers():
            files[member.name] = archive.extractfile(member)

        _assert_common_files(files)
        assert len(files.keys()) == 3 + _common_files_count()

        assert json.loads(files['./manifest.json'].read()) == {'config.json': '1.0',
                                                               'json1.json': '1.1',
                                                               'json2.json': '1.2',
                                                               'json3.json': '1.3'}
    collector._gather_cleanup()


def _assert_common_files(files):
    assert './config.json' in files.keys()
    assert './manifest.json' in files.keys()


def _common_files_count():
    return 2
