# Docker Build
```
docker build -t rankki/bangumi .
sudo docker run -d --env-file .env --name bangumi -v /media:/media -v /aria2-downloads:/downloads -p 6800:6800 -p 6379:6379 rankki/bangumi
```