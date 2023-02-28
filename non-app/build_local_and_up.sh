#!/bin/bash

docker-compose  -f docker-compose.Local.web.app.db.yaml build && docker-compose  -f docker-compose.Local.web.app.db.yaml up

