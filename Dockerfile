FROM python:3.8
RUN apt-get update && apt-get install -y g++
WORKDIR /workdir
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python -m setup install
WORKDIR /
RUN rm -rf /workdir
ENTRYPOINT [ "uwsgi", "--http", ":8000", "--log-5xx", "--disable-logging", "-w", "checkers.webapp:app" ]