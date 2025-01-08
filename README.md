# FastAPI Portal Backend

[![CI](https://github.com/aloong-planet/fastapi-backend/actions/workflows/dev.yaml/badge.svg)](https://github.com/aloong-planet/fastapi-backend/actions/workflows/dev.yaml)

- [FastAPI Portal Backend](#fastapi-portal-backend)
  - [Install poetry](#install-poetry)
  - [Build poetry enviorment](#build-poetry-enviorment)
  - [Run DB Migration](#run-db-migration)
  - [Run FastAPI](#run-fastapi)
  - [Required Tools](#required-tools)
  - [Project Folder Structure](#project-folder-structure)

## Install poetry

Please follow [Poetry Official Installation](https://python-poetry.org/docs/#installation) or [Poetry introduction](https://blog.kyomind.tw/python-poetry/) to install poetry on your localhost.

## Build poetry enviorment

- `poetry config virtualenvs.in-project true` to build .venv folder in repo.
- `poetry env use python` to apply your python path or directly `poetry shell`.
- `poetry install` to install required libs.

## Run DB Migration

- Please modify `.example.env` value and rename as `.env`.

### migration steps:

- First of all, you should sync from the latest alembic migrations from main to your feature branch.
- Run `alembic upgrade head` to update your local databases with the latest changes.
- Run `alembic revision --autogenerate -m "your migration message"` to generate a revision, this step would generate a new migration file under ‘migrations/versions’ folder.
- Check the new generated migration file, if this is not what you expected, just delete this file. If the file is expected, proceed.
- Run `alembic upgrade head` to update your local databases with the new generated revision.
- If you want to roll back the new revision, run `alembic downgrade -1 to rollback`.

## Run FastAPI

- `uvicorn "app.main:app" --reload ` to start server

## Required Tools

- [FastAPI](https://fastapi.tiangolo.com)
- [Pydantic](https://docs.pydantic.dev/latest/)
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [SQLModel](https://sqlmodel.tiangolo.com/help/)
- [alembic](https://alembic.sqlalchemy.org/en/latest/)
- [uvicorn](https://www.uvicorn.org)
- [asyncpg](https://github.com/MagicStack/asyncpg)

## Project Folder Structure

```
|-- app/
    |-- cache/
    |-- configs/
    |-- core/
    |-- database/
    |-- tests/
    |-- utils/
    |-- __init__.py
    |-- apis.py
    |-- crypto.py
    |-- enums.py
    |-- exceptions.py
    |-- log.py
    |-- main.py
    |-- middlewares.py
    |-- models.py
    |-- otel.py
    |-- responses.py
    |-- routers.py
    |-- sorting.py
|-- migrations/
    |-- versions/
    |-- env.py
    |-- script.py.mako
|-- docker-compose/
    |-- .example.env
    |-- docker-compose.yaml
    |-- otel-collector-config.yml
|-- .editorconfig
|-- .gitignore
|-- alembic.ini
|-- Dockerfile
|-- entry.sh
|-- poetry.lock
|-- pyproject.toml
|-- requirements.txt
```

- `app/`: The FastAPI main service folder.
  - `cache/`: For managing redis cache client & session.
  - `configs/`: For managing all of configuration for this project.
  - `core/`: For managing all of service of API server.
  - `database/`: For managing database session & seed. And current only have Postgres.
  - `tests/`: For unit-test folder.
  - `utils/`: For util function based scripts.
  - `apis.py`: For getting all of routers from `core/`.
  - `crypto.py`: For encrypt token.
  - `enums.py`: For defining enums with class by ourseleves.
  - `exceptions.py`: For defining or customizing exceptions with class by ourseleves.
  - `log.py`: For logging related settings.
  - `main.py`: The main script for uvicorn & FastAPI.
  - `middlewares.py`: For defining or customizing middlewares with class by ourseleves.
  - `models.py`: This folder is used to scrapy all of models under the `core/` for alembic.
  - `otel.py`: For auto instrument trace data to OpenTelemetry.
  - `responses.py`: For defining or customizing responses with class by ourseleves.
  - `routers.py`: For defining or customizing routers with class by ourseleves.
  - `sorting.py`: For sorting result from db models to response.
- `migrations/`: Tha alembic migration files folder.
  - `versions/`: This managed by alembic, which will autogenerate migration script with version.
  - `env.py`: The alembic execute main script file.
  - `script.py.mako`: This used to template render to migration script in `version/`
- `docker-compose/`:
  - `.example.env`: The example env file. When you use, try to rename to `.env`.
  - `docker-compose.yaml`: The example of docker-compose.yaml so that we can run server on localhost.
  - `otel-collector-config.yml`: The configuration of otel collector for http and grpc.
- `.editorconfig`: For VSCode format.
- `alembic.ini`: The configuration of alembic.
- `Dockerfile`: For building the server images.
- `entry.sh`: For entry point shell script.
- `poetry.lock`: Used to record all of libs and version for poetry.
- `pyproject.toml`: It's a configuration file that is used by packaging tools.
- `requirements.txt`: Exported from poetry.
