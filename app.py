import streamlit as st
import json
from scraper import fetch_page, find_pages, build_output

st.set_page_config(page_title="Company Website Scraper", layout="centered")

st.title("🔍 Company Website Intelligence Scraper")
st.write("Enter a company website URL to extract structured company information.")

url = st.text_input("Company Website URL", placeholder="https://www.example.com")

if st.button("Run Scraper"):
    if not url:
        st.warning("Please enter a valid URL")
    else:
        with st.spinner("Scraping website..."):
            soup = fetch_page(url)

            if not soup:
                st.error("Failed to fetch website")
            else:
                pages = find_pages(url)
                data = build_output(url, soup, pages)

                st.success("Scraping completed!")

                st.subheader("📄 Extracted Company Info")
                st.json(data)

                st.download_button(
                    label="Download JSON",
                    data=json.dumps(data, indent=4),
                    file_name="company_profile.json",
                    mime="application/json"
                )
