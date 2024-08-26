import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import re
from tqdm import tqdm
import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import spacy

nlp = spacy.load("en_core_web_sm")

class DataScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.visited_urls = set()
        self.data = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        })

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        if parsed_url.scheme in ['http', 'https'] and parsed_url.netloc == self.base_domain:
            return True
        return False

    def get_homepage_links(self):
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            links = set()
            for a_tag in soup.find_all("a", href=True):
                href = a_tag.get("href")
                url = urljoin(self.base_url, href)
                if self.is_valid_url(url) and not re.search(r'privacy|terms', url, re.IGNORECASE):
                    links.add(url)
            return links
        except requests.RequestException as e:
            print(f"Failed to retrieve homepage {self.base_url}: {e}")
            return set()

    def clean_text(self, text):
        text = text.lower()
        doc = nlp(text)
        tokens = []
        for token in doc:
            if not token.is_stop and not token.is_punct and token.is_alpha:
                tokens.append(token.lemma_)
        cleaned_text = " ".join(tokens)
        return cleaned_text

    def scrape_page(self, url):
        print(f"Scraping {url}")
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for footer in soup.find_all('footer'):
                footer.decompose()
            for navbar in soup.find_all('nav'):
                navbar.decompose()
            for header in soup.find_all('header'):
                header.decompose()
            for elementor_header in soup.find_all('div', {'data-elementor-type': 'header'}):
                elementor_header.decompose()

            
            tags = ['p', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
            
            page_content = " ".join([tag.get_text(strip=True) for tag in soup.find_all(tags)])
            
            # Clean the extracted text
            cleaned_content = self.clean_text(page_content)

            self.data.append({'url': url, 'content': cleaned_content})

        except requests.RequestException as e:
            print(f"Failed to retrieve {url}: {e}")

    def scrape_all_links(self):
        homepage_links = self.get_homepage_links()
        print(f"Found {len(homepage_links)} links on the homepage.")
        for link in tqdm(homepage_links):
            if link not in self.visited_urls:
                self.visited_urls.add(link)
                self.scrape_page(link)

def main():
    st.title("Automated Battlecard Generation System")
    st.sidebar.header("Input Details")
    company_name = st.sidebar.text_input("Your Company Name")
    competitior_name = st.sidebar.text_input("Competitor Name")
    company_url = st.sidebar.text_input("Your Company URL")
    competitor_url = st.sidebar.text_input("Competitor URL")
    target_aud = st.sidebar.text_input("Audience")
    
    if st.sidebar.button("Start Analysis"):
        competitior = DataScraper(competitor_url)
        competitior.scrape_all_links()
        company = DataScraper(company_url)
        company.scrape_all_links()
        
        if competitior.data and company.data:
            st.subheader("Competitor Data")
            st.write(pd.DataFrame(competitior.data))
            st.subheader("Company Data")
            st.write(pd.DataFrame(company.data))
            template = """Question: {question}
                      Answer: Compare between {c1} and {c2} companies having subtopics as Strength, Weakness, Opportunities, and Threats"""
            prompt = ChatPromptTemplate.from_template(template)
            model = OllamaLLM(model='llama3.1')
            chain = prompt | model
            st.subheader("Generating Battlecard...")
            battlecard = chain.invoke({"question": f"Generate a battlecard for sales and marketing using data from {company_name} {company.data} and {competitior_name} {competitior.data} related and useful to the {target_aud}",
                                       "c1": f"{company_name}",
                                       "c2": f"{competitior_name}"})
            st.write(battlecard)
        
            st.subheader("Edit Battlecard")
            battlecard = st.text_area("You can edit the battlecard here:", battlecard)
            
            st.download_button(label="Download Battlecard", data=battlecard, file_name="battlecard.txt")
   
            

if __name__ == "__main__":
    main()
