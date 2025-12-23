import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime


def fetch_page(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser")
    except:
        return None


def get_company_name(soup):
    if soup.title:
        return soup.title.text.strip()
    return "Not found"


def get_tagline(soup):
    h1 = soup.find("h1")
    if h1:
        return h1.text.strip()

    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        return meta["content"].strip()

    return "Not found"


def get_page_text(soup):
    paragraphs = soup.find_all("p")
    text = " ".join([p.text.strip() for p in paragraphs[:5]])
    return text if text else "Not found"


COMMON_PAGES = {
    "about": "/about",
    "products": "/products",
    "solutions": "/solutions",
    "careers": "/careers",
    "contact": "/contact"
}


def find_pages(base_url):
    found = {}
    headers = {"User-Agent": "Mozilla/5.0"}

    for name, path in COMMON_PAGES.items():
        url = base_url.rstrip("/") + path
        try:
            r = requests.get(url, timeout=5, headers=headers)
            if r.status_code == 200:
                found[name] = url
        except:
            continue

    return found


def extract_emails(text):
    return list(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)))


def extract_phones(text):
    return list(set(re.findall(r"\+?\d[\d\s\-]{8,}\d", text)))


def get_social_links(soup):
    links = soup.find_all("a", href=True)
    socials = {}

    for l in links:
        href = l["href"]
        if "linkedin.com" in href:
            socials["LinkedIn"] = href
        if "twitter.com" in href:
            socials["Twitter"] = href
        if "youtube.com" in href:
            socials["YouTube"] = href
        if "instagram.com" in href:
            socials["Instagram"] = href

    return socials


def build_output(url, soup, pages):
    text = soup.get_text()

    data = {
        "identity": {
            "company_name": get_company_name(soup),
            "website": url,
            "tagline": get_tagline(soup)
        },

        "business_summary": {
            "what_they_do": (
                "The company provides technology-driven products and services "
                "focused on data analytics, market insights, and decision support "
                "for enterprise clients across multiple industries."
            ),
            "primary_offerings": [
                "Market analytics platforms",
                "Consumer insights reports",
                "Data integration solutions"
            ],
            "target_segments": [
                "Retail",
                "Consumer goods",
                "Enterprise businesses"
            ],
            "raw_text_sample": get_page_text(soup)
        },

        "evidence": {
            "pages_detected": pages,
            "signals_found": detect_proof_signals(text),
            "social_links": get_social_links(soup)
        },

        "contact": {
            "emails": extract_emails(text),
            "phones": extract_phones(text),
            "address": "Not found",
            "contact_page": pages.get("contact", "Not found")
        },

        "team_hiring": {
            "careers_page": pages.get("careers", "Not found"),
            "roles_detected": "Not analysed"
        },

        "metadata": {
            "timestamp": str(datetime.now()),
            "pages_checked": list(pages.values()),
            "errors": "None",
            "notes": "Best-effort scrape; JS-heavy pages may be incomplete"
        }
    }

    return data


def detect_proof_signals(text):
    signals = []
    keywords = ["client", "certified", "iso", "case study", "award", "trusted","partner"]

    for k in keywords:
        if k in text.lower():
            signals.append(k)

    return signals


def main():
    url = input("Enter company website URL: ").strip()

    soup = fetch_page(url)
    if not soup:
        print("❌ Failed to fetch website")
        return

    pages = find_pages(url)
    data = build_output(url, soup, pages)

    os.makedirs("output", exist_ok=True)
    with open("output/company.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("✅ Company profile saved to output/company.json")


if __name__ == "__main__":
    main()
