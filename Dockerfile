FROM python:3.8
RUN apt-get update && apt-get install -y g++ nginx
WORKDIR /workdir
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY setup.py MANIFEST.in ./
COPY checkers/ checkers/
RUN python -m setup install
COPY checkers/static/ /var/www/static/
COPY nginx.conf /usr/local/etc/nginx.conf
COPY uwsgi.ini /usr/local/etc/uwsgi.ini
COPY entrypoint.sh /usr/local/bin
WORKDIR /
RUN rm -rf /workdir
ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]