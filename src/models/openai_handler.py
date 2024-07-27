import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from src.utils.loggingDecorator import log_operation, get_logger

logger = get_logger(__name__)

class OpenAIHandler:
    """
    Manejador para interactuar con la API de OpenAI.

    Esta clase proporciona métodos para inicializar la conexión con OpenAI
    y realizar llamadas a la API para obtener completaciones.

    Attributes:
        api_key (str): Clave API de OpenAI.
        client (OpenAI): Cliente de OpenAI inicializado.
    """

    @log_operation
    def __init__(self):
        """
        Inicializa la instancia de OpenAIHandler.

        Carga la clave API desde un archivo .env y configura el cliente de OpenAI.

        Raises:
            ValueError: Si no se encuentra la clave API de OpenAI en el archivo .env.
        """
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.error("No se encontró la clave API de OpenAI en el archivo .env")
            raise ValueError("No se encontró la clave API de OpenAI. Asegúrate de tener un archivo .env con OPENAI_API_KEY definido.")
        self.client = OpenAI(api_key=self.api_key)
        logger.info("OpenAIHandler inicializado correctamente")

    @log_operation
    def get_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        Obtiene una completación de la API de OpenAI.

        Args:
            messages (List[Dict[str, str]]): Lista de mensajes para la conversación con la API.

        Returns:
            str: Contenido de la respuesta de la API en formato JSON.

        Raises:
            Exception: Si ocurre un error durante la llamada a la API.
        """
        try:
            logger.info(f"Realizando llamada a la API de OpenAI con {len(messages)} mensajes")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=False,
                response_format={"type": "json_object"}
            )
            logger.info("Llamada a la API completada exitosamente")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error en la llamada a la API de OpenAI: {e}")
            return json.dumps({"error": str(e)})