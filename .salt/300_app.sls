{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{% set ds = data.django_settings %}
{% set scfg = salt['mc_utils.json_dump'](cfg) %}

include:
  - makina-projects.{{cfg.name}}.include.configs

{{cfg.name}}-stop-all:
  cmd.run:
    - name: |
            if ! which systemctl >/dev/null 2>&1;then exit 0;fi
            if ! systemctl show {{data.service_name}};then exit 0;fi
            service {{data.service_name}} stop
    - watch_in:
      - mc_proxy: {{cfg.name}}-configs-after
      - cmd: {{cfg.name}}-start-all

postupdate-{{cfg.name}}-cron:
  file.managed:
    - name: "/etc/cron.d/{{cfg.name}}mailman2postfix"
    - contents: |
                */10 * * * * root su -l {{cfg.user}} -c "{{cfg.data_root}}/update_postfix.sh >/dev/null"
    - user: root
    - mode: 700
    - group: root
    - watch:
      - mc_proxy: {{cfg.name}}-configs-post
    - watch_in:
      - cmd: {{cfg.name}}-start-all
postupdate-{{cfg.name}}:
  file.managed:
    - name: "{{cfg.data_root}}/update_postfix.sh"
    - contents: |
            #!/usr/bin/env bash
            export PATH=$PATH:/usr/sbin
            export lists_domain="${lists_domain:-{{data.lists_domain}}}"
            export api_user="${api_user:-{{data.rest_api_user}}}"
            export api_pass="${api_pass:-{{data.rest_api_pass}}}"
            export non_enforced_lists="${non_enforced_lists:-{{data.get('non_enforced_lists', '')}}}"
            set -e
            cd {{data.app_root}}
            . venv/bin/activate
            mailman aliases
            {% if data.enforce_private_policy %}
            sed -i -re "/-(confirm|join|subscribe|request)@/d" "{{data.var_dir}}/data/postfix_lmtp"
            postmap "{{data.var_dir}}/data/postfix_lmtp"
            cd {{cfg.project_root}}
            if [[ -z "${non_enforced_lists}" ]];then
              lists=$(mailman lists -q)
            else
              lists=$(mailman lists -q|egrep -v "${non_enforced_lists}")
            fi
            for list in $lists;do
              PYTHONPATH="$PWD:$PYTHONPATH" mailman \
                  withlist -r enforce_private_policy.enforce $list
            done
            {% endif %}
    - use_vt: true
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - mode: 750
    - watch:
      - mc_proxy: {{cfg.name}}-configs-post
    - watch_in:
      - cmd: {{cfg.name}}-start-all
  cmd.run:
    - name: "{{cfg.data_root}}/update_postfix.sh"
    - use_vt: true
    - user: {{cfg.user}}
    - watch:
      - file: postupdate-{{cfg.name}}
      - mc_proxy: {{cfg.name}}-configs-post
    - watch_in:
      - cmd: {{cfg.name}}-start-all

{{cfg.name}}-start-all:
  cmd.run:
    - name: |
            if ! which systemctl >/dev/null 2>&1;then exit 0;fi
            if ! systemctl show {{data.service_name}};then exit 0;fi
            service {{data.service_name}} start

