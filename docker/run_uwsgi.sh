#!/bin/sh
set -e

uwsgi --ini app/docker/uwsgi.ini
sleep 1
while kill -0 $(cat /tmp/uwsgi.pid); do
    sleep 1
done
echo uWSGI quit unexpectedly >&2
exit 1
