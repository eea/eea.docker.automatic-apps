#!/bin/sh
set -e

touch $HB_PATH
echo "$CRONTAB" > /crontab
nc -lkp 8080 -e echo -e 'HTTP/1.1 200 OK\r\n' &>/dev/null &
crontab /crontab
crond -f -L -
