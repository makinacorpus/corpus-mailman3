#!/usr/bin/env bash
set +e
set -x
{% set cfg = opts['ms_project'] %}
{% set data = cfg.data %}

cd $(dirname $0)
. venv/bin/activate
if ! mailman status|grep stopped;then
    mailman stop
    for i in $(ps afux|egrep "bin/master|bin/runner" |awk '{print $2}');do
        kill -9 $i || /bin/true
    done
else
    exit 0
fi
if mailman status|grep stopped;then
    exit 0
fi
