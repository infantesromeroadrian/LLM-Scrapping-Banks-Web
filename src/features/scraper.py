import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Callable
from src.utils.loggingDecorator import log_operation, get_logger

logger = get_logger(__name__)

class Scraper:
    """
    Clase para realizar scraping de sitios web utilizando diferentes métodos.

    Esta clase proporciona métodos para scrapear sitios web utilizando BeautifulSoup
    y Jina AI, y permite añadir funciones de scraping personalizadas.

    Attributes:
        scrape_functions (List[Dict[str, Callable]]): Lista de funciones de scraping disponibles.
    """

    def __init__(self):
        """
        Inicializa la instancia de Scraper con funciones de scraping predefinidas.
        """
        self.scrape_functions = [
            {"name": "BeautifulSoup", "function": self.beautiful_soup_scrape_url},
            {"name": "JinaAI", "function": self.scrape_jina_ai}
        ]
        logger.info("Scraper inicializado con funciones predefinidas")

    @log_operation
    def beautiful_soup_scrape_url(self, url: str) -> str:
        """
        Scrapea una URL utilizando BeautifulSoup.

        Args:
            url (str): La URL a scrapear.

        Returns:
            str: El contenido HTML de la página scrapeada.

        Raises:
            requests.RequestException: Si ocurre un error al hacer la solicitud HTTP.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            return str(soup)
        except requests.RequestException as e:
            logger.error(f"Error al scrapear {url} con BeautifulSoup: {e}")
            raise

    @log_operation
    def scrape_jina_ai(self, url: str) -> str:
        """
        Scrapea una URL utilizando Jina AI.

        Args:
            url (str): La URL a scrapear.

        Returns:
            str: El contenido de texto de la página scrapeada.

        Raises:
            requests.RequestException: Si ocurre un error al hacer la solicitud HTTP.
        """
        try:
            response = requests.get("https://r.jina.ai/" + url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error al scrapear {url} con Jina AI: {e}")
            raise

    @log_operation
    def get_scrape_functions(self) -> List[Dict[str, Callable[[str], str]]]:
        """
        Obtiene la lista de funciones de scraping disponibles.

        Returns:
            List[Dict[str, Callable[[str], str]]]: Lista de funciones de scraping.
        """
        return self.scrape_functions

    @log_operation
    def add_scrape_function(self, name: str, function: Callable[[str], str]):
        """
        Añade una nueva función de scraping a la lista de funciones disponibles.

        Args:
            name (str): Nombre de la nueva función de scraping.
            function (Callable[[str], str]): La función de scraping a añadir.
        """
        self.scrape_functions.append({"name": name, "function": function})
        logger.info(f"Nueva función de scraping añadida: {name}")