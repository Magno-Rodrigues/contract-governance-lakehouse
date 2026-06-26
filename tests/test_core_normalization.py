"""
Testes das regras de normalização técnica reutilizáveis.

A normalização de contrato é crítica porque contract_number será a chave
de integração entre fontes SGC e NACT.
"""

from src.core.normalization import normalize_contract_number


def test_normalize_contract_number_from_vale_prefix():
    assert normalize_contract_number("VALE5900052656") == "5900052656"


def test_normalize_contract_number_from_alpa_prefix():
    assert normalize_contract_number("ALPA5900065869") == "5900065869"


def test_normalize_contract_number_without_prefix():
    assert normalize_contract_number("5900055119") == "5900055119"


def test_normalize_contract_number_empty_value():
    assert normalize_contract_number("") is None


def test_normalize_contract_number_none():
    assert normalize_contract_number(None) is None