docker-compose -f docker-compose.local.yaml build
docker tag docker_stocks_app:latest 631686326988.dkr.ecr.us-east-1.amazonaws.com/docker_stocks_app:latest
docker push 631686326988.dkr.ecr.us-east-1.amazonaws.com/docker_stocks_app:latest || aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 631686326988.dkr.ecr.us-east-1.amazonaws.com

docker tag docker_stocks_web:latest 631686326988.dkr.ecr.us-east-1.amazonaws.com/docker_stocks_web:latest
docker push 631686326988.dkr.ecr.us-east-1.amazonaws.com/docker_stocks_web:latest || aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 631686326988.dkr.ecr.us-east-1.amazonaws.com


