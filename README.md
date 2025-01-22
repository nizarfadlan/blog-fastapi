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

### Installation with Docker

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

4. Docker Compose (Preferred)

Run the following command to start the application

```bash
docker-compose up -d
```

You should have an api container and postgres container running. Then head to http://127.0.0.1:8000/docs.

### Manual Installation

Steps to run the application manually without Docker, make sure you have the requirements installed.
For the manual installation, you need to have a Postgres database running.

Step 1-3 are the same as the Installation with Docker.

4. Install the dependencies

```bash
poetry install
```

5. Run the migrations

```bash
poetry run alembic upgrade head
```

6. Run the application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

You should have the application running on http://127.0.0.1:8000/docs.

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