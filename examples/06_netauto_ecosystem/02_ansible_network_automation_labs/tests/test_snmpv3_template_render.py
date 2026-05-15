from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = PROJECT_ROOT / "templates"
FIXTURE_FILE = PROJECT_ROOT / "tests" / "fixtures" / "snmpv3_template_vars.yml"


def render_snmpv3_template() -> str:
    template_vars = yaml.safe_load(FIXTURE_FILE.read_text())

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=False,
    )
    template = env.get_template("snmpv3_config.j2")
    return template.render(**template_vars)


def test_snmpv3_template_renders_expected_lines():
    rendered = render_snmpv3_template()

    assert "snmp-server view MONITOR-VIEW iso included" in rendered
    assert "snmp-server group MONITOR-GRP v3 priv read MONITOR-VIEW" in rendered
    assert (
        "snmp-server user SNMPUser1 MONITOR-GRP v3 "
        "auth sha AUTHPASS123 priv aes 128 PRIVPASS123"
    ) in rendered


def test_snmpv3_template_contains_auth_and_priv_keywords():
    rendered_lower = render_snmpv3_template().lower()

    assert "auth sha" in rendered_lower
    assert "priv aes 128" in rendered_lower


def test_snmpv3_template_has_no_unrendered_jinja_expressions():
    rendered = render_snmpv3_template()

    assert "{{" not in rendered
    assert "}}" not in rendered
