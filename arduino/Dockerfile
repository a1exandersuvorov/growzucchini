FROM python:3.11-slim

RUN pip install -U platformio

WORKDIR /project
COPY . .

CMD ["platformio", "run"]