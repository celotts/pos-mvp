"""Tests del mecanismo i18n de mensajes de error/validación del API."""

import pytest

from core.i18n import (
    MESSAGES_EN,
    MESSAGES_ES,
    detect_lang,
    get_current_lang,
    set_current_lang,
    tr,
)


@pytest.fixture(autouse=True)
def _reset_lang():
    """Restaura el idioma por defecto (en) tras cada test para no filtrar estado."""
    set_current_lang("en")
    yield
    set_current_lang("en")


def test_detect_lang_default_english_when_no_header():
    assert detect_lang(None) == "en"
    assert detect_lang("") == "en"


def test_detect_lang_spanish_by_prefix():
    assert detect_lang("es") == "es"
    assert detect_lang("es-ES, en;q=0.9") == "es"
    assert detect_lang("es-MX") == "es"


def test_detect_lang_other_languages_default_english():
    assert detect_lang("fr-FR") == "en"
    assert detect_lang("pt-BR, fr;q=0.8") == "en"


def test_default_language_is_english():
    assert get_current_lang() == "en"


def test_set_current_lang_normalizes_es():
    set_current_lang("es")
    assert get_current_lang() == "es"


def test_set_current_lang_normalizes_other_to_en():
    set_current_lang("fr")
    assert get_current_lang() == "en"
    set_current_lang("en")
    assert get_current_lang() == "en"


def test_tr_uses_context_language():
    set_current_lang("es")
    assert tr("NOT_FOUND.USER") == MESSAGES_ES["NOT_FOUND.USER"]
    set_current_lang("en")
    assert tr("NOT_FOUND.USER") == MESSAGES_EN["NOT_FOUND.USER"]


def test_tr_english_by_default():
    assert get_current_lang() == "en"
    assert tr("NOT_FOUND.USER") == "User not found."


def test_tr_explicit_lang_param_overrides_context():
    assert tr("NOT_FOUND.USER", lang="es") == "Usuario no encontrado."
    assert tr("NOT_FOUND.USER", lang="en") == "User not found."


def test_tr_interpolates_params():
    msg = tr("NOT_FOUND.PRODUCT_ID", product_id="abc-123")
    assert msg == "Product with id abc-123 not found."


def test_tr_missing_key_falls_back_to_key():
    assert tr("NONEXISTENT.KEY") == "NONEXISTENT.KEY"


def test_tr_missing_es_key_falls_back_to_english():
    # Al eliminar una clave de ES artificialmente, se debe caer al inglés.
    saved = MESSAGES_ES.pop("SALE.CANCELLED")
    try:
        set_current_lang("es")
        assert tr("SALE.CANCELLED") == MESSAGES_EN["SALE.CANCELLED"]
    finally:
        MESSAGES_ES["SALE.CANCELLED"] = saved


def test_en_and_es_dictionaries_share_same_key_set():
    assert set(MESSAGES_EN.keys()) == set(MESSAGES_ES.keys())


def test_all_templates_have_no_unbalanced_braces():
    for table in (MESSAGES_EN, MESSAGES_ES):
        for key, template in table.items():
            assert template.count("{") == template.count(
                "}"
            ), f"{key} has unbalanced braces"
