FROM python:3.7-alpine

# Default runtime intervals in seconds
ENV RUN_INTERVALS 120
# Default multiplier since last heartbeat = THRESHOLD_MULTIPLIER * RUN_INTERVALS
ENV THRESHOLD_MULTIPLIER 3
ENV HB_PATH /var/run/a_apps_heartbeat

COPY requirements.txt \
     src /

RUN pip install -r /requirements.txt

HEALTHCHECK --interval=5s --timeout=3s \
    CMD if [ $((`date +%s` - `stat -c %X $HB_PATH`)) -le $(($THRESHOLD_MULTIPLIER*$RUN_INTERVALS)) ]; \
        then echo $((`date +%s` - `stat -c %X $HB_PATH`)) seconds since last heartbeat; else exit 1; fi

ENTRYPOINT  ["/entrypoint.sh"]
