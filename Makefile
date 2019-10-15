POETRY_VERSION := 1.0.0a5

.PHONY: setup build install lint release
DEFAULT: build

setup:
	pip install poetry==$(POETRY_VERSION)
	pip install pre-commit
	pre-commit install-hooks

build:
	poetry build

install: build
	poetry install
	cmus-osx install --force

lint:
	pre-commit run --all-files

release: lint build
	poetry version
	poetry publish
