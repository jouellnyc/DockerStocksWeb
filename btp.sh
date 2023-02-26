#docker-compose  -f docker-compose.local.dev.yaml build 
docker-compose  -f  docker-compose.AWS.hosted.MongoDb.bespoke.yaml  build 
docker tag u2f_app:latest 554829083981.dkr.ecr.us-east-1.amazonaws.com/u2f_app:latest
docker push 554829083981.dkr.ecr.us-east-1.amazonaws.com/u2f_app:latest

