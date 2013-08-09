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
      - mc_proxy: mailman3-configs-after
      - cmd: {{cfg.name}}-start-all

{#
postupdate-{{cfg.name}}:
  cmd.run:
    - name: |
            . venv/bin/activate
            mailman aliases
    - use_vt: true
    - cwd: {{data.app_root}}
    - user: {{cfg.user}}
    - watch:
      - mc_proxy: {{cfg.name}}-configs-post
    - watch_in:
      - cmd: {{cfg.name}}-start-all
#}

{{cfg.name}}-start-all:
  cmd.run:
    - name: |
            if ! which systemctl >/dev/null 2>&1;then exit 0;fi
            if ! systemctl show {{data.service_name}};then exit 0;fi
            service {{data.service_name}} start

