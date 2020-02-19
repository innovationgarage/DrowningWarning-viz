docker service create --mount type=bind,src=/root/data,dst=/app/app/static/files/processed --name dw-app -p 5001:5001 dw-app
