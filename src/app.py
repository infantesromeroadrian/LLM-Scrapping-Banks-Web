import streamlit as st
from src.utils.competitor_sites import CompetitorSites
from src.features.scraper import Scraper
from src.features.content_processor import ContentProcessor
from src.utils.token_cost_calculator import TokenCostCalculator
from src.models.openai_handler import OpenAIHandler
import json


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


def main():
    st.title("Web Scraping and LLM-powered Analysis Tool")

    # Inicializar componentes
    competitor_sites = CompetitorSites("../data/competitor_sites.json")
    scraper = Scraper()
    openai_handler = OpenAIHandler()
    token_calculator = TokenCostCalculator()
    content_processor = ContentProcessor(openai_handler, token_calculator)

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

                # Scraping
                with st.spinner(f"Scraping {selected_site['name']}..."):
                    try:
                        content = scraper.scrape_jina_ai(selected_site['url'])
                        st.success("Scraping successful")
                        st.write(f"Content length: {len(content)} characters")
                    except Exception as e:
                        st.error(f"Error scraping {selected_site['name']}: {str(e)}")
                        return

                # Content processing with LLM
                with st.spinner(f"Analyzing content for {selected_site['name']}..."):
                    try:
                        prompt = f"""Based on the following content from {selected_site['name']}, please answer this question: {user_query}

                        If the question is about pricing or features, please structure your answer as a JSON object with keys for each pricing tier, including 'name', 'price', and 'features' for each tier.

                        Content: {content}"""

                        result = openai_handler.get_completion([{"role": "user", "content": prompt}])
                        result_dict = json.loads(result)
                        st.success("Analysis successful")

                        st.header("Analysis Results")
                        if "answer" in result_dict and isinstance(result_dict["answer"], dict):
                            for tier, details in result_dict["answer"].items():
                                display_pricing_tier(tier, details)
                        else:
                            st.write(result_dict.get("answer", "No structured answer available."))

                        # Mostrar JSON original para referencia
                        with st.expander("Show raw JSON data"):
                            st.json(result_dict)

                    except Exception as e:
                        st.error(f"Error analyzing content for {selected_site['name']}: {str(e)}")

                st.success("Analysis completed")


if __name__ == "__main__":
    main()