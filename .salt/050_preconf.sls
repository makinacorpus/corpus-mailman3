{% set cfg = opts['ms_project'] %}
{% set data = cfg.data %}

include:
  - makina-projects.{{cfg.name}}.include.configs

{{cfg.name}}-reload-systemd:
  cmd.run:
    - watch:
      - mc_proxy: {{cfg.name}}-configs-after
    - unless: |
              if ! which systemctl >/dev/null 2>&1;then exit 0;fi
              if systemctl show {{data.service_name}};then exit 0;fi
    - name: systemctl daemon-reload
