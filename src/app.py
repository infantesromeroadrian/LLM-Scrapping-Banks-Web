import streamlit as st
from src.utils.competitor_sites import CompetitorSites
from src.features.scraper import Scraper
from src.features.content_processor import ContentProcessor
from src.utils.token_cost_calculator import TokenCostCalculator
from src.models.openai_handler import OpenAIHandler
import json


def format_price(price):
    if price is None:
        return "N/A"
    return f"${price:,.2f}"


def display_pricing_tier(tier_name, tier_data):
    st.subheader(tier_name)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Plan Name", tier_data["name"])
    with col2:
        st.metric("Price", format_price(tier_data["price"]))


def main():
    st.title("Web Scraping and Price Analysis Tool")

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

            # Botón para ejecutar el análisis
            if st.button("Run Analysis"):
                st.subheader(f"Analyzing {selected_site['name']}")

                # Scraping
                with st.spinner(f"Scraping {selected_site['name']}..."):
                    try:
                        content = scraper.beautiful_soup_scrape_url(selected_site['url'])
                        st.success("Scraping successful")
                        st.write(f"Content length: {len(content)} characters")
                    except Exception as e:
                        st.error(f"Error scraping {selected_site['name']}: {str(e)}")
                        return

                # Content processing
                with st.spinner(f"Processing content for {selected_site['name']}..."):
                    try:
                        result = content_processor.extract(content)
                        result_dict = json.loads(result)
                        st.success("Content processing successful")

                        st.header("Pricing Analysis Results")

                        # Mostrar resultados en un formato más atractivo
                        display_pricing_tier("Cheapest Offer", result_dict["cheapest"])
                        display_pricing_tier("Mid-range Offer", result_dict["middle"])
                        display_pricing_tier("Most Expensive Offer", result_dict["most_expensive"])

                        # Calcular y mostrar el rango de precios
                        min_price = min(tier["price"] for tier in result_dict.values() if tier["price"] is not None)
                        max_price = max(tier["price"] for tier in result_dict.values() if tier["price"] is not None)
                        st.info(f"Price Range: {format_price(min_price)} - {format_price(max_price)}")

                        # Mostrar JSON original para referencia
                        with st.expander("Show raw JSON data"):
                            st.json(result_dict)

                    except Exception as e:
                        st.error(f"Error processing content for {selected_site['name']}: {str(e)}")

                st.success("Analysis completed")


if __name__ == "__main__":
    main()