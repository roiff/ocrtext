安装docker
进入工程目录,执行如下代码,开启docker即可
如碰到安装源等问题,可以自行修改安装源,或者FQ解决.
```
git clone https://github.com/roiff/ocrtext.git
docker build -t ocrtext:v1 .
docker run -d --net host -p 8099:8099 --name ocrtext ocrtext:v1
```
接口地址:
http://ip:[port]/api/ocrtext/
默认端口8099

接口方式:
header: 
content-type: multipart/form-data

body:
file: 上传的图片
boxarr: 需要识别的区域,例如:[[x1,y1,x2,y2],[x1,y1,x2,y2]]
whitelist: 白名单,填写时,只识别白名单中的字符串,例如:"测试1234567890"

附录中TS_Test_Script为触动精灵中的测试模块和脚本,直接拿来用就好了