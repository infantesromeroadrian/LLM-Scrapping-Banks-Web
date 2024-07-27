import tiktoken
from src.utils.loggingDecorator import log_operation, get_logger

logger = get_logger(__name__)

class TokenCostCalculator:
    """
    Clase para calcular el costo de tokenización de texto.

    Esta clase proporciona métodos para contar tokens y calcular el costo
    asociado basado en un modelo de precios por millón de tokens.

    Attributes:
        cost_per_million_tokens (float): Costo por millón de tokens.
        tokenizer: Instancia del tokenizador de tiktoken.
    """

    def __init__(self, cost_per_million_tokens: float = 5):
        """
        Inicializa la instancia de TokenCostCalculator.

        Args:
            cost_per_million_tokens (float): Costo por millón de tokens. Por defecto es 5.
        """
        self.cost_per_million_tokens = cost_per_million_tokens
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            logger.info("Tokenizador inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar el tokenizador: {e}")
            raise

    @log_operation
    def count_tokens(self, input_string: str) -> int:
        """
        Cuenta el número de tokens en una cadena de entrada.

        Args:
            input_string (str): Cadena de texto a tokenizar.

        Returns:
            int: Número de tokens en la cadena de entrada.
        """
        try:
            tokens = self.tokenizer.encode(input_string)
            return len(tokens)
        except Exception as e:
            logger.error(f"Error al contar tokens: {e}")
            raise

    @log_operation
    def calculate_cost(self, input_string: str) -> float:
        """
        Calcula el costo de tokenización para una cadena de entrada.

        Args:
            input_string (str): Cadena de texto para calcular el costo.

        Returns:
            float: Costo calculado para la tokenización de la cadena de entrada.
        """
        try:
            num_tokens = self.count_tokens(input_string)
            total_cost = (num_tokens / 1_000_000) * self.cost_per_million_tokens
            return total_cost
        except Exception as e:
            logger.error(f"Error al calcular el costo: {e}")
            raise