import json
from typing import List, Dict, Any
from src.utils.loggingDecorator import log_operation, get_logger
from src.utils.token_cost_calculator import TokenCostCalculator

logger = get_logger(__name__)

class ContentProcessor:
    """
    Clase para procesar contenido y extraer información de precios.

    Esta clase proporciona métodos para dividir contenido en chunks,
    procesar el contenido con OpenAI y extraer información de precios.

    Attributes:
        openai_handler (OpenAIHandler): Instancia del manejador de OpenAI.
        token_calculator (TokenCostCalculator): Instancia del calculador de costos de tokens.
    """

    def __init__(self, openai_handler: Any, token_calculator: TokenCostCalculator):
        """
        Inicializa la instancia de ContentProcessor.

        Args:
            openai_handler (Any): Instancia del manejador de OpenAI.
            token_calculator (TokenCostCalculator): Instancia del calculador de costos de tokens.
        """
        self.openai_handler = openai_handler
        self.token_calculator = token_calculator
        logger.info("ContentProcessor inicializado")

    @staticmethod
    @log_operation
    def chunk_content(content: str, max_tokens: int = 4000) -> List[str]:
        """
        Divide el contenido en chunks más pequeños.

        Args:
            content (str): Contenido a dividir.
            max_tokens (int): Número máximo de tokens por chunk.

        Returns:
            List[str]: Lista de chunks de contenido.
        """
        words = content.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word.split()) > max_tokens:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(word)
            current_length += len(word.split())

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        logger.info(f"Contenido dividido en {len(chunks)} chunks")
        return chunks

    @staticmethod
    def get_valid_price(tier: Dict[str, Any]) -> float | None:
        """
        Obtiene un precio válido de un tier.

        Args:
            tier (Dict[str, Any]): Diccionario que representa un tier de precio.

        Returns:
            float | None: Precio válido o None si no se encuentra un precio válido.
        """
        return tier.get("price") if tier and isinstance(tier.get("price"), (int, float)) else None

    @log_operation
    def extract(self, user_input: str) -> str:
        """
        Extrae información de precios del contenido proporcionado.

        Args:
            user_input (str): Contenido del cual extraer información de precios.

        Returns:
            str: JSON string con la información de precios extraída.
        """
        entity_extraction_system_message = {
            "role": "system",
            "content": "Get me the three pricing tiers from this website's content, and return as a JSON with three keys: {cheapest: {name: str, price: float}, middle: {name: str, price: float}, most_expensive: {name: str, price: float}}. If you can't find a price, use null for the price value."
        }

        chunks = self.chunk_content(user_input)
        all_results = []

        for i, chunk in enumerate(chunks):
            logger.info(f"Procesando chunk {i+1}/{len(chunks)}")
            messages = [
                entity_extraction_system_message,
                {"role": "user", "content": chunk}
            ]
            try:
                result = json.loads(self.openai_handler.get_completion(messages))
                all_results.append(result)
            except json.JSONDecodeError:
                logger.error(f"Error al decodificar JSON para el chunk {i+1}")

        try:
            final_result = {
                "cheapest": min(
                    (r["cheapest"] for r in all_results if "cheapest" in r),
                    key=lambda x: self.get_valid_price(x) or float("inf")
                ),
                "most_expensive": max(
                    (r["most_expensive"] for r in all_results if "most_expensive" in r),
                    key=lambda x: self.get_valid_price(x) or float("-inf")
                )
            }

            all_prices = [
                tier for r in all_results for tier in [r.get("cheapest"), r.get("middle"), r.get("most_expensive")]
                if tier and self.get_valid_price(tier) is not None
            ]
            all_prices.sort(key=lambda x: self.get_valid_price(x))
            final_result["middle"] = all_prices[len(all_prices) // 2] if all_prices else None

            logger.info("Extracción de precios completada exitosamente")
            return json.dumps(final_result)
        except Exception as e:
            logger.error(f"Error al procesar los resultados finales: {e}")
            return json.dumps({"error": "No se pudo extraer la información de precios"})