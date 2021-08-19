FROM python:3.6

LABEL Author="roiff<github.com/roiff>"

COPY . /ocrtext
WORKDIR /ocrtext

RUN pip3 install --user -U pip -i https://pypi.doubanio.com/simple/  --trusted-host pypi.doubanio.com 

RUN pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/  --trusted-host mirrors.aliyun.com 

CMD python3 backend/main.py
