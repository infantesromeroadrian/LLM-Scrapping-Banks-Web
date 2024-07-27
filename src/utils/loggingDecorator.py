import logging
from functools import wraps

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_operation(func):
    """
    Decorador para registrar las operaciones realizadas en una clase.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        logger.info(f"Ejecutando {func.__name__} con args: {args}, kwargs: {kwargs}")
        result = func(self, *args, **kwargs)
        logger.info(f"{func.__name__} completado")
        return result
    return wrapper

def get_logger(name):
    """
    Obtiene un logger configurado para un módulo específico.

    Args:
        name (str): Nombre del módulo para el cual se quiere obtener el logger.

    Returns:
        logging.Logger: Logger configurado para el módulo especificado.
    """
    return logging.getLogger(name)