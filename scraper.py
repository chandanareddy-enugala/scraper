import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import json

def determine_selector(url):
    match = re.search(r'/release/(\d+\.\d+)/', url)
    if match:
        version_number = float(match.group(1))
        if 10.0 <= version_number <= 16.2:
            return '.sect1'
        elif 1.0 <= version_number < 10.0:
            return '.SECT1'
    return '.SECT1'

def scrape_urls(base_url):
    response = requests.get(base_url)
    if response.ok:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=True)
        
        url_selector_list = []
        for link in links:
            url = urljoin(base_url, link['href'])
            selector = determine_selector(url)
            url_selector_list.append({'url': url, 'selector': selector})

        with open('new_url_selectors.json', 'w') as file:
            json.dump(url_selector_list, file)

        print("URLs and their selectors have been saved to new_url_selectors.json")
    else:
        print("Failed to retrieve the web page")

def scrape_content():
    with open('new_url_selectors.json', 'r') as file:
        url_selectors_list = json.load(file)

    for url_selector in url_selectors_list:
        url = url_selector['url']
        selector = url_selector['selector']
        print(f"Scraping {url} with selector {selector}")

        response = requests.get(url)
        if response.ok:
            soup = BeautifulSoup(response.content, 'html.parser')
            content_container = soup.select_one(selector)
            if content_container:
                formatted_text = []
                for element in content_container.find_all(['h1', 'h2', 'p', 'ul', 'li', 'span', 'dt']):
                    if element.name == 'h1':
                        formatted_text.append(f"# {element.get_text()}\n")
                    elif element.name == 'h2':
                        formatted_text.append(f"## {element.get_text()}\n")
                    elif element.name == 'p':
                        formatted_text.append(f"{element.get_text()}\n")
                    elif element.name == 'li':
                        formatted_text.append(f"* {element.get_text()}\n")

                text_to_write = "".join(formatted_text)

                release_name_match = re.search(r'/release/(.+?)/', url)
                release_name = release_name_match.group(1) if release_name_match else "unknown_release"

                filename = f"content_{release_name}.txt"
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(text_to_write)
                print(f"File created: {filename}")
            else:
                print(f"No content found for the selector {selector} in the URL {url}")
        else:
            print(f"Failed to retrieve the web page for {url}")

# Example usage
base_url = "https://www.postgresql.org/docs/release/"
scrape_urls(base_url)
scrape_content()

