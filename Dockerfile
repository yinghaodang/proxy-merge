FROM python:3.9

WORKDIR /root/

COPY proxy_merge.py main.py requirements.txt /root/

COPY utils /root/utils

RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD uvicorn main:app --host 0.0.0.0 --port 8000 --reload
