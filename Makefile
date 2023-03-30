# get your token on pypi.org
# export pypi_token="your token"
TOKEN = ${pypi_token}

.DEFAULT:
.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep | sed 's/^/\n/' | sed 's/#/\n/'

.PHONY: lint
lint:  ## run black, autopep, flake8
	find . -iname "*.py" -exec black {} \;
	find . -iname "*.py" -exec autopep8 --in-place {} \;
	flake8 --ignore=E501,W503

.PHONY: test
test: lint  ## run pytest and lint
	pip3 install pytest pytest-mock mock mocker django
	pytest -s -v

.PHONY: publish
build: test  ## run pytest and lint nad build package
	rm -rvf dist/*
	pip3 install trove-classifiers ptyprocess msgpack lockfile distlib tomlkit tomli shellingham rapidfuzz pyrsistent poetry-core platformdirs pkginfo pexpect packaging jeepney jaraco.classes filelock dulwich crashtest cachecontrol virtualenv SecretStorage jsonschema cleo keyring poetry-plugin-export poetry
	python3 -m pip install --upgrade build
	python3 -m pip install --upgrade twine
	python3 -m build

.PHONY: build  
publish: build  ## publish package to pypi
	echo -e "[pypi]\n  username = __token__\n  password = ${TOKEN}" > ~/.redhat-pypirc
	python3 -m twine upload --verbose --non-interactive --config-file ~/.redhat-pypirc --repository pypi dist/*