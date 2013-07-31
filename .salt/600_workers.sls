{% import "makina-states/services/monitoring/circus/macros.jinja" as circus with context %}
{% set cfg = opts.ms_project %}
{% set data = cfg.data %}

include:
  - makina-projects.{{cfg.name}}.include.configs

{{cfg.name}}-services:
  cmd.run:
    - name: echo
  service.running:
    - names: [{{data.service_name}}]
    - enable: true
    - watch:
      - mc_proxy: {{cfg.name}}-configs-after
      - cmd: {{cfg.name}}-services
