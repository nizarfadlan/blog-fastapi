# Blog FastApi

This is a simple blog API using FastAPI and Postgres.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Installation with Docker](#installation-with-docker)
  - [Manual Installation](#manual-installation)
- [Seed Data](#seed-data)
- [Testing](#testing)

## Features

- Create, read, update and delete article/content
- Create, read, update and delete users
- Create, read, and update roles

## Requirements

- Python 3.11
- Poetry ^2.0.1
- Postgres 16

## Installation

1. Clone the repository

```bash
git clone https://github.com/nizarfadlan/blog-fastapi.git
```

3. Copy the `.env.example` file to `.env` and fill in the required environment variables

```bash
cp .env.example .env
```

Generate a secret key for the `SECRET_KEY` environment variable

```bash
openssl rand -hex 32
```

`ENVIRONMENT` should be set to `local`, `staging` and `production`, default is `local`


### With Docker

4. Docker Compose (Preferred)

Run the following command to start the application

```bash
docker-compose up -d
```

You should have an api container and postgres container running. Then head to http://127.0.0.1:8000/docs.

### Manual

Steps to run the application manually without Docker, make sure you have the requirements installed.

To run this project, ensure you have PostgreSQL installed and running on your local machine.
Next, configure the following settings in the `.env` file according to your local PostgreSQL database details:

- `POSTGRES_USER`: Your database username.  
- `POSTGRES_PASSWORD`: Your database password.  
- `POSTGRES_SERVER`: Your database server address (usually `localhost` if running locally).  
- `POSTGRES_PORT`: Your database port (default: `5432`).  
- `POSTGRES_DB`: The name of the database to be used.  

Make sure these values match your local PostgreSQL database configuration.

4. Install the dependencies

```bash
poetry install
```

5. Apply the migrations

```bash
poetry run alembic upgrade head
```

6. Run the application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should have the application running on http://127.0.0.1:8000/docs.

## Migration

To create a new migration, run the following command

```bash
poetry run alembic revision --autogenerate -m "migration message"
```

To apply the migration, run the following command

```bash
poetry run alembic upgrade head
```

## Seed Data

To seed the database with some initial data, run the following command

```bash
poetry run seed
```

## Testing

To run the tests, run the following command

```bash
poetry run test
```