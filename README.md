# Web

## Dependencies

* [Docker](https://www.docker.com/).
* [Docker Compose](https://docs.docker.com/compose/install/).
* [Poetry](https://python-poetry.org/) for Python package and environment management.

## Config

* Create ".env" file and add environment variables to it:
```dotenv
# base
SECRET_KEY=some-secret-key
PROJECT_NAME=some-project-name

# databases
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_DB=postgres
POSTGRES_TEST_DB=test
PGDATA=/var/lib/postgresql/data/pgdata
```
* To generate hex 32 hex SECRET_KEY:
```console
$ openssl rand -hex 32
```

* Other project settings you can see in "app/core/config.py"

## Development

* Run server with all dependencies:

```console
$ docker-compose up --build
```
* Add pre-commit hook

```console
$ pre-commit install
```

## Tests

Testing is done with pytest, tests are placed in the "tests" directory

For testing, you should go inside the container and run the command `pytest .`

```console
$ docker exec -it <FastAPI container ID> bash
$ pytest .
```

## Project structure

```
-> *app*
   -> *api* — layer with logic for processing requests via api
   -> *core* — global things for the project, like settings (`config.py`)
   -> *db* — database and session initialization
   -> *models* — models in SQLAlchemy terminology (not to be confused with *schemas* in pydantic and business models)
   -> *schemas* — schemes for validating/serializing request/response objects (they are also models in pydantic terminology)
   -> *services* — service layer, all business logic is placed here.
   -> *utils* — utility logic.
-> *tests* — root for tests
-> *.env.template* — file to list all environment variables used inside the service
```

## Migrations

* After creating the model in `app/models`, you need to import it in `app/db/base.py` (in order to make it visible to alembic)
* Make migrations (run inside container)

```console
$ alembic -n postgres revision --autogenerate -m "add column last_name to User model"
```

* Run migrations

```console
$ alembic -n postgres upgrade head
```

* Postgres
```console
$ alembic -n postgres revision --autogenerate -m "text"
$ alembic -n postgres upgrade head
$ alembic -n postgres downgrade -1
```
