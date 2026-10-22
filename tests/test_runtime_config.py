import pytest

from zotero_arxiv_daily.runtime_config import apply_legacy_environment


def test_legacy_settings_preserve_original_scope_and_mail_server(config):
    apply_legacy_environment(config, {
        "ARXIV_QUERY": "cs.DC+cs.PF,cs.AR+cs.DC",
        "SMTP_SERVER": "smtp.example.org", "SMTP_PORT": "587",
        "MAX_PAPER_NUM": "-1", "LANGUAGE": "Chinese",
    })
    assert list(config.source.arxiv.category) == ["cs.DC", "cs.PF", "cs.AR"]
    assert config.email.smtp_server == "smtp.example.org"
    assert config.email.smtp_port == 587
    assert config.executor.max_paper_num == -1
    assert config.llm.language == "Chinese"


def test_custom_config_takes_precedence_over_legacy_settings(config):
    apply_legacy_environment(config, {"CUSTOM_CONFIG": "source: {}", "ARXIV_QUERY": "cs.DC", "SMTP_PORT": "465"})
    assert list(config.source.arxiv.category) == ["cs.AI", "cs.CV"]
    assert config.email.smtp_port == 1025


def test_invalid_legacy_query_does_not_expose_value(config):
    with pytest.raises(ValueError) as error:
        apply_legacy_environment(config, {"ARXIV_QUERY": "private-value/invalid"})
    assert "private-value" not in str(error.value)


def test_empty_legacy_values_preserve_config(config):
    apply_legacy_environment(config, {"ARXIV_QUERY": "", "SMTP_PORT": "", "LANGUAGE": ""})
    assert config.email.smtp_port == 1025


@pytest.mark.parametrize("value", ["0", "-2"])
def test_invalid_paper_limit(config, value):
    with pytest.raises(ValueError, match="positive integer"):
        apply_legacy_environment(config, {"MAX_PAPER_NUM": value})
