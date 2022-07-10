# Docker Build
```
docker build -t rankki/bangumi .
sudo docker run -d --env-file .env --name bangumi -v /media:/media -v /aria2-downloads:/downloads rankki/bangumi
```