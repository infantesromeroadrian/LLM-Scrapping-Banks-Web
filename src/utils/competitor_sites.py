import json
import os
from typing import List, Dict
from src.utils.loggingDecorator import log_operation, get_logger

logger = get_logger(__name__)


class CompetitorSites:
    def __init__(self, filename: str):
        self.filename = filename
        self.sites = self.load_sites()
        logger.info(f"CompetitorSites inicializado con el archivo {filename}")

    @log_operation
    def load_sites(self) -> List[Dict[str, str]]:
        try:
            # Asegurarse de que el directorio existe
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)

            # Intentar abrir el archivo
            with open(self.filename, 'r') as file:
                sites = json.load(file)
            logger.info(f"Sitios cargados exitosamente desde {self.filename}")
            return sites
        except FileNotFoundError:
            logger.warning(f"Archivo {self.filename} no encontrado. Creando nuevo archivo.")
            return []
        except json.JSONDecodeError:
            logger.error(f"Error al decodificar JSON desde {self.filename}. Iniciando con lista vacía.")
            return []

    @log_operation
    def save_sites(self):
        try:
            # Asegurarse de que el directorio existe
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)

            with open(self.filename, 'w') as file:
                json.dump(self.sites, file, indent=4)
            logger.info(f"Sitios guardados exitosamente en {self.filename}")
        except IOError as e:
            logger.error(f"Error al guardar sitios en {self.filename}: {str(e)}")
            raise

    @log_operation
    def add_site(self, name: str, url: str):
        new_site = {"name": name, "url": url}
        self.sites.append(new_site)
        self.save_sites()
        logger.info(f"Sitio añadido: {new_site}")

    def get_sites(self) -> List[Dict[str, str]]:
        return self.sites