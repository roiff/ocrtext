安装docker
进入工程目录,执行如下代码,开启docker即可
如碰到安装源等问题,可以自行修改安装源,或者FQ解决.
```
git clone https://github.com/roiff/ocrtext.git
cd ocrtext
docker build -t ocrtext:v1 .
docker run -d --net host -p 8099:8099 --name ocrtext ocrtext:v1
```

接口地址:
识别文字: http://ip:[port]/api/ocrtext/
查找文字: http://ip:[port]/api/findtext/
默认端口8099

接口方式:
header: 
content-type: multipart/form-data

识别文字:

body:

ile: 上传的图片

boxarr: 需要识别的区域,例如:[[x1,y1,x2,y2],[x1,y1,x2,y2]]

whitelist: 白名单,填写时,只识别白名单中的字符串,例如:"测试1234567890"

查找文字:

body:

file: 上传的图片

whitelist: 选填,白名单,填写时,只识别白名单中的字符串,例如:"测试1234567890"

compress 选填,图像压缩比,把图像的短边(图像中较短的边长)压缩成对应数值进行查找,不填写时短边大于960时,压缩成960,否则不压缩,注意!!!该参数会影响文本框的识别,如在图像较大,文字较小时,可以调整参数,提高准确率,参数越小,速度越快.一般情况可以不填写,或者填写nil

match 选填,图像匹配模式,只有再有白名单的时候才生效,默认为false,即只要在白名单中出现的字符串都列出,当参数为true时,仅查找和白名单完全匹配的字符串.

附录中TS_Test_Script为触动精灵中的测试模块和脚本,直接拿来用就好了
