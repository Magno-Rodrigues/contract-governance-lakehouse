import time
from typing import Callable, Any


def execute_with_retry(
    operation: Callable,
    max_retries: int,
    delay_seconds: int,
    *args,
    **kwargs
) -> Any:
    """
    Executa operação com retry automático.

    Estratégia:
    ----------
    Se ocorrer exception, tenta novamente até atingir
    o número máximo de tentativas.

    Parameters
    ----------
    operation : Callable
        Função que será executada.

    max_retries : int
        Número máximo de tentativas.

    delay_seconds : int
        Tempo de espera entre tentativas.

    Returns
    -------
    Any
        Resultado da operação.

    Raises
    ------
    Exception
        Relança último erro se todas falharem.
    """

    last_error = None

    for attempt in range(max_retries):

        try:
            return operation(
                *args,
                **kwargs
            )

        except Exception as error:

            last_error = error

            if attempt < max_retries - 1:
                time.sleep(delay_seconds)

    raise last_error