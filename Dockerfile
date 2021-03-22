FROM python:3.8
RUN apt-get update && apt-get install -y g++
WORKDIR /workdir
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python -m setup install
WORKDIR /
RUN rm -rf /workdir
ENTRYPOINT [ "gunicorn", "-b", "0.0.0.0:8000", "checkers.webapp:app" ]