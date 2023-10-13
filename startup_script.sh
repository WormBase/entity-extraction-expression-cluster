#!/usr/bin/env bash

declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env
chmod 0644 /etc/cron.d/expr-cluster-ext-cron
touch /var/log/expr-cluster_ext_pipeline.log
crontab /etc/cron.d/expr-cluster-ext-cron
cron

tail -f /dev/null