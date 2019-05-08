#!/bin/sh
set -e

touch $HB_PATH
echo "$CRONTAB" > /crontab

crontab /crontab
crond -f -L -
