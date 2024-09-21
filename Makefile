APPLICATION_NAME := thumbnail-api
APPLICATION_VERSION ?= 0.1.0
DOCKER_IMAGE_TAG ?= ${APPLICATION_NAME}:${APPLICATION_VERSION}
PYTHON_COMMAND := python3
REQUIRED_PYTHON_VERSION := 3.12.6
REQUIRED_PIPX_VERSION := 1.7.1
REQUIRED_POETRY_VERSION := 1.8.3

Prefix = make $@:
Entrypoint = app/srv

run: install-dependencies
	poetry run fastapi dev $(Entrypoint)

test: install-dependencies
	poetry run pytest -m "not slow" $(loc)

test-all: install-dependencies
	poetry run pytest

format: install-dependencies
	@echo "$(Prefix) Formatting files..."
	poetry run ruff format .

type-check: install-dependencies
	@echo "$(Prefix) Performing type checking analysis..."
	poetry run mypy .

pre-commit: format type-check

build-docker:
	docker build -t ${DOCKER_IMAGE_TAG} .
	# docker build -t $(shell poetry version | tr ' ' ':') .

deploy: build-docker
	kind load docker-image ${APPLICATION_NAME}:${APPLICATION_VERSION}
	helm upgrade --install ${APPLICATION_NAME} helm-chart

clean:
	rm -fr tests/acceptance_test_artifacts task_queue_data .coverage htmlcov


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
	@echo "$(Prefix) Syncing virtual environment with locked dependencies..."
	poetry install --only main,dev --no-root --sync
	@echo "$(Prefix) Done installing dependencies"

