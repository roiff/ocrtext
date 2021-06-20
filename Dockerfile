FROM python:3.6

LABEL Author="roiff<github.com/roiff>"

COPY . /ocrtext
WORKDIR /ocrtext

RUN pip3 install --user -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple/  \ 
    && pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/ 

CMD python3 backend/main.py
