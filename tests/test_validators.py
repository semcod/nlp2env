from nlp2env.validators import (
    validate_api_key,
    validate_bool,
    validate_email,
    validate_host,
    validate_key_value,
    validate_port,
    validate_url,
)


def test_validate_email_ok():
    assert validate_email("a@b.cc")["ok"] is True


def test_validate_email_fail():
    assert validate_email("not-an-email")["ok"] is False


def test_validate_host_ip():
    assert validate_host("192.168.1.1")["ok"] is True


def test_validate_host_domain():
    assert validate_host("smtp.gmail.com")["ok"] is True


def test_validate_host_fail():
    assert validate_host("not a host!!!")["ok"] is False


def test_validate_port_ok():
    assert validate_port("587")["ok"] is True


def test_validate_port_fail():
    assert validate_port("70000")["ok"] is False


def test_validate_url_ok():
    assert validate_url("https://api.example.com")["ok"] is True


def test_validate_url_fail():
    assert validate_url("not-a-url")["ok"] is False


def test_validate_bool_ok():
    assert validate_bool("true")["ok"] is True
    assert validate_bool("0")["ok"] is True


def test_validate_bool_fail():
    assert validate_bool("maybe")["ok"] is False


def test_validate_api_key_openai():
    assert validate_api_key("sk-test123", field="OPENAI_API_KEY")["ok"] is True


def test_validate_api_key_groq():
    assert validate_api_key("gsk-test123", field="GROQ_API_KEY")["ok"] is True


def test_validate_key_value_email():
    result = validate_key_value("SMTP_USER", "bad")
    assert result is not None
    assert result["ok"] is False


def test_validate_key_value_host():
    result = validate_key_value("SMTP_HOST", "localhost")
    assert result is not None
    assert result["ok"] is True


def test_validate_key_value_no_validator():
    assert validate_key_value("CUSTOM_VAR", "anything") is None
