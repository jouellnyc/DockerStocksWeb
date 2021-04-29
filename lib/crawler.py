#!/usr/bin/env python3

FROM python:3.7

ARG WORKDIR=/stocks/
ARG MY_ENTRY=crawler.entry.sh
ARG MY_PY3=/usr/bin/python3

RUN apt-get update  -y && \
    apt-get install -y --no-install-recommends vim \
    curl \
    net-tools \
    less \
    telnet \
    net-tools  &&  pip install --upgrade pip

RUN mkdir /$WORKDIR/
COPY requirements.txt /$WORKDIR/
RUN pip3 install -r /$WORKDIR/requirements.txt

RUN mkdir /$WORKDIR/non-app/   && \
    mkdir /$WORKDIR/static/    && \
    mkdir /$WORKDIR/templates/ && \
    mkdir /$WORKDIR/lib/       && \
    mkdir -p /$WORKDIR/external/gunicorn/

COPY non-app/  /$WORKDIR/non-app/
COPY lib/      /$WORKDIR/lib/

COPY Docker/$MY_ENTRY  /usr/sbin/$MY_ENTRY

RUN chown -R nobody:  /$WORKDIR/  &&     \
    chmod 755 /usr/sbin/$MY_ENTRY &&     \
    rm $MY_PY3                    &&     \
    ln -s /usr/local/bin/python3 $MY_PY3

USER nobody
ENTRYPOINT /usr/sbin/crawler.entry.sh
EXPOSE 8000
