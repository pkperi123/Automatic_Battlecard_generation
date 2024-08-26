Documentation: Automated Battlecard Generation System
Overview
The Automated Battlecard Generation System is a tool designed to scrape competitor websites, process the textual data, and generate customizable battlecards focused on sales and marketing. The system leverages web scraping techniques, Natural Language Processing (NLP), and a generative AI model Llama3.1 to automate the creation of battlecards. The output is tailored to specific target audiences, helping marketing and sales teams effectively position their products or services.
Components

Class: DataScraper

Attributes:

base_url: The competitor's website URL.

base_domain: The domain of the competitor's website.

visited_urls: A set to keep track of visited URLs.

data: A list to store the scraped and processed data.

session: A requests session to manage HTTP requests.

Methods:

is_valid_url(url): Validates if a URL belongs to the competitor's domain.

get_homepage_links(): Retrieves all valid links from the competitor's homepage, excluding links to privacy policy and terms of service pages.

clean_text(text): Cleans and processes the text by removing stopwords, punctuation, and lemmatizing words.

scrape_page(url): Scrapes content from a given page, removing unnecessary elements like headers, footers, and navigation bars, and then processes the text.

scrape_all_links(): Scrapes all pages linked from the homepage.

Main Application:

Streamlit Interface:

company_name: Input field for the user's company name.
competitor_name : Input field for the competitor name.
company_url : Input field for the user’s company website URL.
competitor_url: Input field for the competitor's website URL.
target_aud: Input field for specifying the target audience.
A button to start the analysis and initiate scraping and battlecard generation.

Battlecard Generation:
The scraped and cleaned data is used as input for a prompt template.
The prompt is processed by the Llama3.1 AI model to generate a battlecard between two companies, focusing on Strengths, Weaknesses, Opportunities, and Threats (SWOT).
The generated battlecard can be edited and downloaded as a text file.

Usage
Installation:
Cmd: pip install -r requirements.txt

Packages used

langchain

langchain-ollama

langchain_experimental

beautifulsoup4

pandas

streamlit

spacy

ollama

Cmd: ollama pull lllama3.1


Execution:

cmd:	streamlit run app.py
