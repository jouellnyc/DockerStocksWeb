#/bin/bash
docker exec -it $(docker ps | grep -i stocks_app | awk '{ print $1; }') cat /tmp/*err*
