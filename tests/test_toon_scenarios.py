from pathlib import Path

from nlp2env.toon_scenarios import load_scenarios, parse_testtoon


def test_parse_testtoon_meta():
    text = """# SCENARIO: demo
# TYPE: nlp2env
# VERSION: 1.0

PROMPTS[1]{id, lang, source, nl, tool, after, assert_configured}:
  pl-1, pl, llm, "Ustaw SMTP", -, -, false

ASSERT_ENV[1]{prompt_id, expect}:
  pl-1, SMTP_HOST=smtp.example.com
"""
    script = parse_testtoon(text)
    assert script.meta["scenario"] == "demo"
    assert script.meta["type"] == "nlp2env"
    scenarios = load_scenarios_from_text(text)
    assert len(scenarios) == 1
    assert scenarios[0].prompt_id == "pl-1"
    assert scenarios[0].fields["lang"] == "pl"
    assert scenarios[0].expects == ["SMTP_HOST=smtp.example.com"]


def load_scenarios_from_text(text: str):
    from nlp2env.toon_scenarios import scenarios_from_toon

    return scenarios_from_toon(parse_testtoon(text))


def test_load_inline_example():
    path = Path(__file__).resolve().parents[1] / "examples/write/smtp-email/smtp-email-inline.testql.toon.yaml"
    scenarios = load_scenarios(path)
    assert len(scenarios) == 5
    status = next(s for s in scenarios if s.prompt_id == "status-check")
    assert status.assert_configured is True
    assert status.tool == "nlp2env_email_status"
