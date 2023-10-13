FROM python:3.8-slim

RUN apt-get update && apt-get install -y cron

WORKDIR /usr/src/app/
ADD requirements.txt .
RUN pip3 install -r requirements.txt
RUN python3 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
COPY . .

ENV DB_HOST=""
ENV DB_NAME=""
ENV DB_USER=""
ENV DB_PASSWD=""
ENV SSH_USER=""
ENV SSH_PASSWD=""
ENV SSH_HOST=""
ENV FROM_DATE="19700101"
ENV WORKING_DIR=""

ADD crontab /etc/cron.d/expr-cluster-ext-cron

ENV PYTHONPATH=$PYTHONPATH:/usr/src/app/

CMD ["/bin/bash", "startup_script.sh"]
