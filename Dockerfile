FROM python:3.12.0

WORKDIR /backend

COPY pyproject.toml /backend/

RUN python -m pip install --upgrade pip \
  && python -m pip install poetry \
  && poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

ADD . /backend

EXPOSE 8080

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
