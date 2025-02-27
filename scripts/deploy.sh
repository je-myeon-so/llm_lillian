sudo docker ps -a -q --filter "name=app" | grep -q . && docker stop app && docker rm app | true

sudo docker rmi kkolbuyw/jemyeonso-fastapi:latest

sudo docker pull kkolbuyw/jemyeonso-fastapi:latest

docker run -d -v /home/ubuntu/env/.env:/fastapi/src/.env -p 8080:8000 --env-file .env --name app kkolbuyw/jemyeonso-fastapi:latest

docker rmi -f $(docker images -f "dangling=true" -q) || true
