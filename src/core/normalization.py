"""
Funções reutilizáveis de normalização técnica.

Este módulo concentra regras simples e estáveis usadas por várias camadas
do lakehouse.

A principal regra neste momento é a normalização do número de contrato,
pois contract_number é a chave de integração entre SGC e NACT.
"""

import re
from typing import Optional


def normalize_contract_number(value: Optional[str]) -> Optional[str]:
    """
    Normaliza número de contrato.

    Exemplos:
    - "VALE5900052656" -> "5900052656"
    - "ALPA5900065869" -> "5900065869"
    - "5900055119"     -> "5900055119"

    Regra:
    Mantém apenas dígitos.
    """

    if value is None:
        return None

    value_as_text = str(value)

    digits_only = re.sub(
        r"\D",
        "",
        value_as_text,
    )

    if digits_only == "":
        return None

    return digits_only