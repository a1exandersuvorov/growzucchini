FROM python:3.12

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install

COPY . .

CMD ["poetry", "run", "python", "main.py"]
