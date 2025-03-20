import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


class SearchEngineScraper:
    """
    Class searching for a query on a given Seach Engine and returning the results' links and text of the first page
    """

    def __init__(self, search_engine: str = "https://html.duckduckgo.com/html"):
        options = Options()
        options.add_argument("--headless=new")
        self.browser = webdriver.Chrome(options=options)
        self.browser.get(search_engine)
        if search_engine == "https://www.google.com/":
            self.__cookies_check_reject()

    def __cookies_check_reject(self):
        """For google.com, checks for cookies and reject them, irrelevant for duckduckgo.com, and as google is blocked by captcha, not used"""
        try:
            WebDriverWait(self.browser, 100).until(
                EC.element_to_be_clickable((By.ID, "W0wltc"))
            )
            cookies_button_reject = self.browser.find_element(By.ID, "W0wltc")
            cookies_button_reject.click()
        except Exception as e:
            print(f"Error: {e}")
            print("No cookies button found")

    def search(self, query: str):
        """
        Search for a query on the given search engine and return the results
        """

        # Wait for the search field to be present
        WebDriverWait(self.browser, 100).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_text_field = self.browser.find_element(By.NAME, "q")
        search_text_field.clear()
        search_text_field.send_keys(query)
        search_text_field.submit()

        # Wait for the results to be present
        WebDriverWait(self.browser, 100).until(
            EC.presence_of_element_located((By.CLASS_NAME, "result"))
        )
        results = self.browser.find_elements(By.CLASS_NAME, "result")
        urls = []
        descriptions = []

        # Iterate over results and extract the url and the description
        for result in results:
            url = result.find_element(By.TAG_NAME, "a")
            description = result.find_element(By.CLASS_NAME, "result__snippet")
            descriptions.append(description.text)
            urls.append(url.get_attribute("href"))
        return dict(zip(urls, descriptions))

    def search_multiple(self, query):
        """
        Searches for multiple queries and return the results
        """

        # Check if query is a string or a list, if is a string, convert to list
        if isinstance(query, str):
            query = [query]
        # Search for the query and save the results as a dictionary
        ret = {}
        for q in query:
            res = self.search(q)
            ret.update(res)
        
        return ret


    def search_multiple_to_JSON(self, query, file_name: str):
        """
        Searches for multiple queries and outputs them to a json file
        """
        # Search for the queries
        to_save = self.search_multiple(query)

        # Create file if does not exist
        if not os.path.exists(file_name):
            with open(self.file_name, "w+") as file:
                json.dump({}, file)

        # Load the file
        data = {}
        with open(file_name, "r") as file:
            data = dict(json.load(file))

        # Update the file with the new data
        data.update(to_save)

        # Override the file
        with open(file_name, "w") as file:
            json.dump(data, file)

    def get_query_results_text(self, query: str):
        """
        Gets the search query first 10 results text of the website.
        """

        # Search the query
        results = self.search(query)

        # Get all the articles from a page
        relevant_text = []
        for url in results.keys():
            try:
                # Use beautiful soup to get the text
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Safari/537.36"
                }
                html = requests.get(url, headers=headers).text
                soup = BeautifulSoup(html, "lxml")
                soup = soup.find_all("article")
                relevant_text.extend(soup)
            except:
                # Try using selenium to get the text
                print(f"Couldn't get {url}, continuing with selenium")
                self.browser.get(url)
                self.browser.implicitly_wait(10)
                elems = self.browser.find_elements(By.TAG_NAME, "article")
                for el in elems:
                    relevant_text.append(el.text)

        # Extract the text from all the paragraphs
        texts = []
        for text in relevant_text:
            if isinstance(text, str):
                soup = BeautifulSoup(text, "lxml")
            else:
                soup = BeautifulSoup(text.text, "lxml")

            texts.append(soup.get_text())
        return texts


if __name__ == "__main__":
    scraper = SearchEngineScraper()
    #    print(scraper.search('javascript'))
    print(scraper.get_query_results_text("Python"))
#    print(scraper.search_multiple(['python', 'c++']))
#    scraper.search_multiple_to_JSON(['python', 'c#'], 'test.json')
