import streamlit as st
from src.utils.competitor_sites import CompetitorSites
from src.features.scraper import Scraper
from src.features.content_processor import ContentProcessor
from src.utils.token_cost_calculator import TokenCostCalculator
from src.models.openai_handler import OpenAIHandler
from src.features.evaluation import Evaluator
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_price(price):
    if price is None or price == "Custom":
        return price
    try:
        return f"${float(price):,.2f}"
    except ValueError:
        return price


def display_pricing_tier(tier_name, tier_data):
    st.subheader(tier_name)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Plan Name", tier_data.get("name", "N/A"))
    with col2:
        st.metric("Price", format_price(tier_data.get("price", "N/A")))

    if "features" in tier_data:
        st.write("Features:")
        for feature in tier_data["features"]:
            st.write(f"- {feature}")


def display_evaluation_results(evaluation):
    st.subheader("Evaluation Results")
    st.metric("Accuracy", f"{evaluation['accuracy']:.2%}")

    if evaluation["missing_info"]:
        st.write("Missing Information:")
        for info in evaluation["missing_info"]:
            st.write(f"- {info}")

    if evaluation["incorrect_info"]:
        st.write("Incorrect Information:")
        for info in evaluation["incorrect_info"]:
            st.write(f"- {info}")

    if evaluation["extra_info"]:
        st.write("Extra Information:")
        for info in evaluation["extra_info"]:
            st.write(f"- {info}")


def main():
    st.title("Web Scraping and LLM-powered Analysis Tool")

    # Inicializar componentes
    competitor_sites = CompetitorSites("../data/competitor_sites.json")
    scraper = Scraper()
    openai_handler = OpenAIHandler()
    token_calculator = TokenCostCalculator()
    content_processor = ContentProcessor(openai_handler, token_calculator)
    evaluator = Evaluator()

    # Sidebar para añadir nuevos sitios
    st.sidebar.header("Add New Competitor Site")
    new_site_name = st.sidebar.text_input("Site Name")
    new_site_url = st.sidebar.text_input("Site URL")
    if st.sidebar.button("Add Site"):
        if new_site_name and new_site_url:
            competitor_sites.add_site(new_site_name, new_site_url)
            st.sidebar.success(f"Added {new_site_name}")
        else:
            st.sidebar.error("Please enter both site name and URL")

    # Main page
    st.header("Competitor Sites")
    sites = competitor_sites.get_sites()
    if not sites:
        st.warning("No competitor sites added yet. Please add a site using the sidebar.")
    else:
        # Crear una lista de nombres de sitios para el selectbox
        site_names = [site['name'] for site in sites]
        selected_site_name = st.selectbox("Select a site to analyze", site_names)

        # Encontrar el sitio seleccionado
        selected_site = next((site for site in sites if site['name'] == selected_site_name), None)

        if selected_site:
            st.write(f"Selected site: **{selected_site['name']}** - {selected_site['url']}")

            # Campo de entrada para la pregunta del usuario con ejemplo
            st.write("What information would you like to extract? (Enter your question below)")
            user_query = st.text_input(
                "Example: What are the pricing tiers and their features?",
                "What are the pricing tiers and their features?"
            )

            # Botón para ejecutar el análisis
            if st.button("Run Analysis"):
                st.subheader(f"Analyzing {selected_site['name']}")

                # Ejemplo de expected_result (actualizado para Mindsmith AI)
                expected_result = {
                    "Free": {
                        "name": "Free",
                        "price": "$0",
                        "features": [
                            "Create unlimited lessons",
                            "Two active shared lessons",
                            "Generate five lessons",
                            "Authoring tool",
                            "Share via link, SMS, email, iframe",
                            "Export dynamic eLearning modules (SCORM)",
                            "Review and comment links",
                            "Unlimited learners",
                            "AI lesson assistant",
                            "Custom theming",
                            "Basic chat and email support"
                        ]
                    },
                    "Professional": {
                        "name": "Professional",
                        "price": "$39",
                        "features": [
                            "Unlimited active lessons",
                            "GPT-4 model",
                            "Unlimited premium generations",
                            "Granular lesson analytics",
                            "Basic customer support",
                            "Add your logo",
                            "Remove 'Built with Mindsmith' tag",
                            "Multi-language lessons"
                        ]
                    },
                    "Team": {
                        "name": "Team",
                        "price": "Custom",
                        "features": [
                            "Shared team workspace",
                            "Branding management tools",
                            "Multi-language lessons",
                            "Personalized+priority customer support",
                            "Export lesson analytics to pdf",
                            "Real-time lesson collaboration",
                            "Share lessons on a custom domain",
                            "Content development assistance",
                            "Turnkey eLearning development outsourcing"
                        ]
                    }
                }

                # Scraping y análisis
                with st.spinner(f"Analyzing {selected_site['name']}..."):
                    try:
                        # Aquí usamos el evaluador para obtener tanto el resultado como la evaluación
                        evaluation_result = evaluator.evaluate_response(selected_site['name'], user_query,
                                                                        expected_result)

                        if "error" in evaluation_result:
                            st.error(f"Error: {evaluation_result['error']}")
                            return

                        result_dict = evaluation_result["raw_response"]
                        st.success("Analysis successful")

                        st.header("Analysis Results")
                        if "answer" in result_dict and isinstance(result_dict["answer"], dict):
                            for tier, details in result_dict["answer"].items():
                                display_pricing_tier(tier, details)
                        else:
                            st.write(result_dict.get("answer", "No structured answer available."))

                        # Logging para diagnóstico
                        logger.info(f"Expected result: {json.dumps(expected_result, indent=2)}")
                        logger.info(f"Generated result: {json.dumps(result_dict.get('answer', {}), indent=2)}")
                        logger.info(f"Evaluation result: {json.dumps(evaluation_result, indent=2)}")

                        # Mostrar resultados de la evaluación
                        display_evaluation_results(evaluation_result)

                        # Mostrar JSON original para referencia
                        with st.expander("Show raw JSON data"):
                            st.json(result_dict)

                    except Exception as e:
                        st.error(f"Error analyzing content for {selected_site['name']}: {str(e)}")
                        logger.exception("Error during analysis")

                st.success("Analysis completed")


if __name__ == "__main__":
    main()