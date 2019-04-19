FROM python:2.7-alpine

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY main.py /

ENTRYPOINT ["/main.py"]
