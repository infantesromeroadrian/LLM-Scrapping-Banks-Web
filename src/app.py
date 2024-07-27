import streamlit as st
from src.utils.competitor_sites import CompetitorSites
from src.features.scraper import Scraper
from src.features.content_processor import ContentProcessor
from src.utils.token_cost_calculator import TokenCostCalculator
from src.models.openai_handler import OpenAIHandler
import json


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
        for site in sites:
            st.write(f"**{site['name']}**: {site['url']}")

    # Scraping and analysis
    if st.button("Run Analysis"):
        if not sites:
            st.error("No sites to analyze. Please add at least one site.")
        else:
            for site in sites:
                st.subheader(f"Analyzing {site['name']}")

                # Scraping
                with st.spinner(f"Scraping {site['name']}..."):
                    try:
                        content = scraper.beautiful_soup_scrape_url(site['url'])
                        st.success("Scraping successful")
                        st.write(f"Content length: {len(content)} characters")
                    except Exception as e:
                        st.error(f"Error scraping {site['name']}: {str(e)}")
                        continue

                # Content processing
                with st.spinner(f"Processing content for {site['name']}..."):
                    try:
                        result = content_processor.extract(content)
                        st.success("Content processing successful")
                        st.json(json.loads(result))
                    except Exception as e:
                        st.error(f"Error processing content for {site['name']}: {str(e)}")

            st.success("Analysis completed for all sites")


if __name__ == "__main__":
    main()