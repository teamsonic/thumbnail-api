APPLICATION_NAME := thumbnail-api
PYTHON_COMMAND := python3
REQUIRED_PYTHON_VERSION := 3.12.6
REQUIRED_PIPX_VERSION := 1.7.1
REQUIRED_POETRY_VERSION := 1.8.3

Prefix = make $@:
Entrypoint = src/cmd/main.py


check-python-installed:
	@echo "$(Prefix) Checking installed python version..."
	@./functions.sh command_exists ${PYTHON_COMMAND}; \
	if [ $$? -ne 0 ]; \
	then \
		echo "$(Prefix) Could not find a python installation."; \
		echo "$(Prefix) Please visit 'https://www.python.org/downloads' and install Python version ${REQUIRED_PYTHON_VERSION} or later"; \
		echo "$(Prefix) If the python installation is not on the PATH, rerun the MAKE target with 'PYTHON_EXECUTABLE_NAME' set to the path of the executable"; \
		echo "$(Prefix) e.g. make PYTHON_EXECUTABLE_NAME=/path/to/python"; \
		exit 1; \
	fi

check-python-version: check-python-installed
	@echo "$(Prefix) Checking python version..."
	@./functions.sh version_gte $(shell ${PYTHON_COMMAND} --version | cut -d " " -f2) ${REQUIRED_PYTHON_VERSION}; \
	if [ $$? -ne 0 ]; \
	then \
	    echo "$(Prefix) Installed Python version does not meet minimum version requirement of ${REQUIRED_PYTHON_VERSION}"; \
	    echo "$(Prefix) Please visit 'https://www.python.org/downloads' and install Python version ${REQUIRED_PYTHON_VERSION} or later"; \
	    exit 1; \
	else \
  		echo "$(Prefix) Python version up to date"; \
	fi

install-pipx: check-python-version
	@echo "$(Prefix) Checking for a pipx installation..."
	@./functions.sh command_exists pipx; \
	if [ $$? -ne 0 ]; \
	then \
		echo "$(Prefix) Installing pipx..."; \
		brew install pipx; \
	fi
	@pipx ensurepath
	@echo "$(Prefix) pipx installed"

update-pipx: install-pipx
	@echo "$(Prefix) Checking installed pipx version..."
	@./functions.sh version_gte $(shell pipx --version) ${REQUIRED_PIPX_VERSION}; \
	if [ $$? -ne 0 ]; \
	then \
		echo "$(Prefix) Upgrading pipx to latest version..."; \
		brew update && brew upgrade pipx; \
	fi
	@echo "$(Prefix) pipx version up to date"

install-poetry: update-pipx
	@echo "$(Prefix) Checking for a poetry installation"
	@./functions.sh command_exists poetry; \
	if [ $$? -ne 0 ]; \
	then \
	  	echo "$(Prefix) Installing poetry..."; \
		pipx install poetry; \
	fi
	@echo "$(Prefix) poetry installed"

update-poetry: install-poetry
	@echo "$(Prefix) Checking installed poetry version..."
	@./functions.sh version_gte $(poetry about | grep -e "^Version" | cut -d ' ' -f2) ${REQUIRED_POETRY_VERSION}; \
	if [ $$? -ne 0 ]; \
	then \
	  	echo "$(Prefix) Upgrading poetry to latest version..."; \
		poetry self update; \
	fi
	@echo "poetry version up to date"

install-dependencies: update-poetry
	@echo "$(Prefix) Ensuring environment has dependencies installed..."
	@poetry install --only main,dev --no-root
	@echo "$(Prefix) Done installing dependencies"

format: install-dependencies
	@echo "$(Prefix) Formatting files..."
	@poetry run ruff format .

type-check: install-dependencies
	@echo "$(Prefix) Performing type checking analysis..."
	@poetry run mypy .


build: update-poetry
	@echo "$(Prefix) Building application..."
	@poetry build --format wheel

run: update-poetry
	@poetry run fastapi dev $(Entrypoint)

test: update-poetry
	@poetry run pytest -m "not slow"

test-long: update-poetry
	@poetry run pytest -m "slow"

test-acceptance: update-poetry
	@poetry run pytest -m "acceptance"

test-all: update-poetry
	@poetry run pytest

build-docker:
	docker build -t $(shell poetry version | tr ' ' ':') .
	# Ensure docker is installed
	# Build a new docker image if one does not exist or if application code has been updated

build-chart:
	# Build a chart archive if one does not exist or if chart has been updated

kind:
	# Ensure kind cluster is up

deploy:
	# Ensure docker image has been built
	# Ensure chart archive has been built
	# Ensure kind cluster can be connected to
	# Install Helm chart
