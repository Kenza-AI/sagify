.PHONY: help
help:
	@echo "clean-pyc: remove Python file artifacts"
	@echo "lint: check style with flake8"
	@echo "test: run tests quickly with the default Python"
	@echo "test-all: run tests on every Python version with tox"

.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

.PHONY: lint
lint:
	flake8

.PHONY: test
test:
	py.test tests/

.PHONY: test-all
test-all:
	tox

