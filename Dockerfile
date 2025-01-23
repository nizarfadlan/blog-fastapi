FROM python:3.11-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry
RUN poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-slim

WORKDIR /code

RUN apt-get update && apt-get install -y netcat-openbsd

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN chmod +x /code/entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["sh", "/code/entrypoint.sh"]
