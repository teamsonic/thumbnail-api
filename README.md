# thumbnail-api
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

thumbnail-api is a web application written in python that creates thumbnails from user-uploaded images.

Maintainer: Josh Burns (josh.burns65@gmail.com)

## Table of Contents
- [Technologies](#technologies)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Limitations](#limitations)
- [Advanced Usage](#advanced-usage)
- [License](#license)

## Technologies
- [FastAPI](https://fastapi.tiangolo.com/) High-performance, easy-to-use web framework
- [Pydantic](https://docs.pydantic.dev/latest/) Data validation library
- [Poetry](https://python-poetry.org/) Python package and dependency manager enabling deterministic builds and development environment
- ~~[Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html) A task queue to distribute work~~ This application actually runs a homebrew task queue distributing work across threads
- [Pytest](https://docs.pytest.org/en/stable/) Python testing framework
- [Mypy](https://mypy.readthedocs.io/en/stable/index.html) Static type checker
- [Ruff](https://docs.astral.sh/ruff/) Lightning-fast Python linter and code formatter
- [GNU make](https://www.gnu.org/software/make/manual/make.html) Unified entrypoint to executing common development and build tasks
- [Docker](https://www.docker.com/) Containerization
- [Helm](https://helm.sh/) Kubernetes package manager

## Usage
- [Clone the Repository](#clone-the-repository)
- [Install Dependencies](#install-dependencies)
- [Launch the FastAPI Server](#launch-the-fastapi-server)
- [Creating Thumbnails](#creating-thumbnails)

### Clone the repository:
```bash
git clone git@github.com:teamsonic/thumbnail-api.git
```

### Install Dependencies
- [Python ^3.12.6](#install-python)
- [Poetry ^1.8.3](#install-poetry)

#### Install Python
Python ^3.12.6 is required. You can check which version is installed on your system with:
```bash
python -V
``` 
or
```bash
python3 -V
```
If the output is `Python 3.12.6` or above you're all set! 

If you need to install Python, you can do it [here](https://www.python.org/downloads/).

#### Install Poetry
Poetry is used for Python dependency management. You can check if you have it installed with:
```bash
poetry --version
```
If the output is `Poetry (version 1.8.3)` or above you should be good to go.
Otherwise, if you're on Mac and have [brew](https://brew.sh/) installed, you can also try the experimental command:
```bash
make update-poetry
```
Which will install and update Poetry via [pipx](https://pipx.pypa.io/stable/).

There are other options to install Poetry, which you can learn more about in its [documentation](https://python-poetry.org/docs/).


If you have an outdated version of Poetry installed, you can update Poetry with the following command:
```bash
poetry self update
``` 

### Launch the FastAPI Server
This project is built on the [FastAPI](https://fastapi.tiangolo.com/) framework. To start the server, run:
```bash
make run
```
This make target will have Poetry sync your virtual environment with the dependencies in the `poetry.lock` file
and then launch the server, which will be reachable at http://127.0.0.1:8000.

### Creating Thumbnails
Once the FastAPI server is running, you can access the interactive API docs at http://127.0.0.1:8000/docs and 
use the `/upload_image` endpoint to submit an image to be converted to a thumbnail; the server will 
begin processing the image and return a `job_id` associated with this task.

Using this `job_id`, make a request to the `/check_job_status/{job_id}` endpoint. If the job is complete,
the thumbnail will be displayed. Otherwise, the current status of the job will be sent back, which can be
either "Processing" or "Error". 

## Running Tests
This project uses the [pytest](https://docs.pytest.org/en/stable/) framework for testing. An easy way to run 
all unit tests is with:
```bash
make test
```
To run the acceptance tests, use:
```bash
make test-acceptance
```
Note that the acceptance tests create a Docker container running the application, so Docker will
first need to be [installed](https://docs.docker.com/get-started/get-docker/) and running.

To run everything at once, use:
```bash
make test-all
```
Coverage reports are automatically generated after each test and available at `htmlcov/index.html`

## Kubernetes Deployment
- [Install Deploy Dependencies](#install-deploy-dependencies)
- [Image Build](#image-build)
- [Deploy](#deploy)

### Install Deploy Dependencies
- [Docker 19.03](https://docs.docker.com/engine/install/) or later (for buildx support).
- [Helm 3.16.1](https://helm.sh/docs/intro/install/) for rendering and deploying Kubernetes manifests.

### Image Build
It's easy to build a Docker image of thumbnail-api:
```bash
make build-docker
```
By default, this will tag the image with the name and current version of the application. You can provide you own tag
like so:
```bash
make build-docker tag=mytag
```

Note that docker's extended build capabilities "[buildx](https://docs.docker.com/reference/cli/docker/buildx/)" are required. 
If you get an error during the build, make sure that `Docker 19.03` or later is installed with `docker -v`.

### Deploy

If you have a [kind](https://kind.sigs.k8s.io/) cluster up and running, you can perform a quick deploy with 
the experimental command:
```bash
make kind-deploy
```
This will:
1. Build the Docker image
2. Load the Docker image into the kind cluster
3. Install the release into the kind cluster using Helm.

If you are not using kind or want to customize the helm deployment, you'll need to run the helm install manually after
adding the Docker image to one of your cluster's registries.

```bash
helm install thumbnail-api helm-chart
```

## Limitations
* FastAPI only runs on port 8000. This can be mitigated by Docker host-container port mapping or using a Kubernetes service as a proxy.
* The app cannot be reliably horizontally scaled to handle increased load, as each application instance uses its own filesystem storage to manage thumbnail processing state. It's possible to mount the same PersistentVolume on multiple pods running this application -- allowing multiple Workers to process tasks from the queue simultaneously -- but the behavior is not tested and could result in multiple workers processing the same task, which would be self-defeating.
* Relatedly, even if horizontal scaling was supported, because the application and the worker run within the same process, they cannot be scaled independently.
* Uploaded images and saved thumbnails do not have a retention policy associated with them, meaning eventually the application will run out of available space and start logging errors everytime an image is uploaded.
* The only supported task store type is the filesystem (no support for databases, key/value stores, etc.)
* Healthcheck endpoint does not report on the operational status of the worker thread -- only if the API server is reachable and responsive. However, the worker thread's status is visible in the application logs.

## Advanced Usage

### Logging
On application startup, the `log_conf.yaml` file will be parsed and used as the logging configuration. The default logging
level is INFO for all logs, but this can be adjusted to your preferences. Be aware that setting the level to DEBUG will
result in the worker outputting events to the log at an average rate of 2 events/second.

### Environment Variables
Any global settings in `app/__init__.py` are overridden at runtime by matching values set in the `.env` file.

## License

[MIT](https://choosealicense.com/licenses/mit/)