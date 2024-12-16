FROM python:3.10-slim

RUN pip install flask pyyaml requests

WORKDIR /usr/src/app

COPY run.sh /run.sh
COPY app.py /app.py
COPY ui.html /ui.html

RUN chmod +x /run.sh

EXPOSE 8080

CMD [ "/run.sh" ]

