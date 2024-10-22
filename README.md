# LLM-Scrapping: Web Scraping and Price Analysis Tool

## Descripción del Proyecto

LLM-Scrapping es una herramienta de web scraping y análisis de precios que utiliza modelos de lenguaje de gran escala (LLM) para extraer y analizar información de precios de sitios web competidores. Esta herramienta está diseñada para ayudar a las empresas a mantener un seguimiento de los precios de la competencia de manera eficiente y automatizada.

## Características Principales

- Web scraping de sitios competidores utilizando BeautifulSoup y Jina AI.
- Análisis de contenido utilizando OpenAI GPT para extraer información de precios.
- Interfaz de usuario interactiva construida con Streamlit.
- Gestión de sitios competidores con almacenamiento en JSON.
- Cálculo de costos de tokenización para estimar gastos de API.

## Flujo de Trabajo

El siguiente diagrama muestra el flujo de trabajo de la herramienta:

```mermaid
graph TD
    A[Inicio] --> B[Identificar sitios web objetivo]
    B --> C[Usar Jira AI para crear tareas de scraping]
    C --> D[Ejecutar web scraping]
    D --> E[Procesar contenido scrapeado con LLM]
    E --> F[Extraer información relevante]
    F --> G[Actualizar tareas de Jira con resultados]
    G --> H[Analizar y reportar resultados]
    H --> I[Fin]

    subgraph "Proceso de Scraping"
    D --> D1[Scraper BeautifulSoup]
    D --> D2[Scraper Jina AI]
    D --> D3[Scraper Personalizado]
    end

    subgraph "Procesamiento LLM"
    E --> E1[Dividir contenido en chunks]
    E1 --> E2[Procesar con OpenAI API]
    E2 --> E3[Extraer información de precios]
    end
```

Este diagrama ilustra el proceso completo desde la identificación de sitios web objetivo hasta el análisis y reporte de resultados, incluyendo los pasos detallados del proceso de scraping y procesamiento con LLM.

## Requisitos del Sistema

- Python 3.8+
- pip o poetry para la gestión de dependencias

## Instalación

1. Clona el repositorio:
   ```
   git clone https://github.com/infantesromeroadrian/LLM-Scrapping-Banks-Web.git
   cd LLM-Scrapping
   ```

2. Instala las dependencias:
   Si usas pip:
   ```
   pip install -r requirements.txt
   ```
   Si usas poetry:
   ```
   poetry install
   ```

3. Configura las variables de entorno:
   Crea un archivo `.env` en la raíz del proyecto y añade tu clave API de OpenAI:
   ```
   OPENAI_API_KEY=tu_clave_api_aqui
   ```

## Uso

Para ejecutar la aplicación:

```
streamlit run src/app.py
```

La aplicación se abrirá en tu navegador predeterminado. Desde allí, podrás:

1. Añadir nuevos sitios competidores para analizar.
2. Ver la lista de sitios competidores.
3. Ejecutar análisis de precios en los sitios añadidos.

## Estructura del Proyecto

```
LLM-Scrapping/
│
├── src/
│   ├── models/
│   │   └── competitor_sites.py
│   ├── features/
│   │   ├── scraper.py
│   │   └── content_processor.py
│   ├── utils/
│   │   ├── logging_utils.py
│   │   ├── token_cost_calculator.py
│   │   └── openai_handler.py
│   └── app.py
│
├── data/
│   └── competitor_sites.json
│
├── tests/
│
├── docs/
│
├── notebooks/
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── pyproject.toml
```

## Contribuir

Las contribuciones son bienvenidas. Por favor, sigue estos pasos para contribuir:

1. Haz un fork del repositorio.
2. Crea una nueva rama para tu característica (`git checkout -b feature/AmazingFeature`).
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`).
4. Haz push a la rama (`git push origin feature/AmazingFeature`).
5. Abre un Pull Request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## Contacto

Adrian Infantes - [@adrianinfantes](https://www.linkedin.com/in/adrianinfantes/) - infantesromeroadrian@gmail.com

Link del Proyecto: [https://github.com/infantesromeroadrian/LLM-Scrapping-Banks-Web](https://github.com/infantesromeroadrian/LLM-Scrapping-Banks-Web)