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
RUN chmod 0644 /etc/cron.d/expr-cluster-ext-cron
RUN touch /var/log/expr-cluster_ext_pipeline.log
RUN crontab /etc/cron.d/expr-cluster-ext-cron

ENV PYTHONPATH=$PYTHONPATH:/usr/src/app/

CMD echo $DB_HOST > /etc/expr-cluster_ext_db_host && \
    echo $DB_NAME > /etc/expr-cluster_ext_db_name && \
    echo $DB_USER > /etc/expr-cluster_ext_db_user && \
    echo $DB_PASSWD > /etc/expr-cluster_ext_db_passwd && \
    echo $MAX_NUM_PAPERS > /etc/expr-cluster_ext_max_num_papers && \
    echo $SSH_USER > /etc/expr-cluster_ext_ssh_user && \
    echo $SSH_PASSWD > /etc/expr-cluster_ext_ssh_passwd && \
    echo $SSH_HOST > /etc/expr-cluster_ext_ssh_host && \
    echo $FROM_DATE > /etc/expr-cluster_ext_from_date && \
    echo $WORKING_DIR > /etc/expr-cluster_ext_working_dir && \
    cron && tail -f /dev/null
