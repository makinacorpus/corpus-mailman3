{% set cfg = opts.ms_project %}
{% set data = cfg.data %}

include:
  - makina-states.services.mail.postfix.hooks
  - makina-projects.{{cfg.name}}.include.configs
  {% if data.postfix %}
  - makina-states.services.mail.postfix
  {% endif %}

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
      - mc_proxy: postfix-postconf
