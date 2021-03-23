#!/bin/bash
nginx -c /usr/local/etc/nginx.conf &
uwsgi /usr/local/etc/uwsgi.ini &
wait -n