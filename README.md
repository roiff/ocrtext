```
docker build -t ocrtext:v1 .
docker run -d --net host --rm -p 8089:8089 --name ocrtext ocrtext:v1
```
