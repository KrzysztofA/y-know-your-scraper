from SearchEngineScraper import SearchEngineScraper
from nltk import tokenize
from openai import Client
import json
import re 


class RelationFinder:
    """
    Class used to perform searches on different relations between the main keyword and the relation
    """
    def __init__(self, keyword: str, base_url: str = "http://localhost:11434/v1", model: str="phi4", temperature: int = 0, api_key:str="ollama", reasoning_model=False):
        self.scraper = SearchEngineScraper()
        self.llm = Client(
                    base_url=base_url,
                    api_key=api_key
        )
        self.key = keyword
        self.model = model
        self.temperature = temperature
        self.reasoning_model = reasoning_model

    def __tokenize_text(self):
        """Tokenize given text and return the number of tokens"""
        pass

    def find_verbose_relation(self, relation):
        """Find desired relation about the given main key, and build an article explaining the relation"""
        relation_data = self.scraper.get_query_results_text(f"{self.key} {relation}")
        main_msg = f"""Extract the following data point: \"{relation}\", about the: \"{self.key}\"\n
                       From this pile of text:\n
                       {relation_data},
                       prepare a verbose and detailed article on \"{relation}\" for a business report with as many details as you can find in the given text about the \"{self.key}.
                       Make sure the article is professional. Don't include any preambles, nor any acknowledgements or anything besides the article.
                    """
        msgs = [
        {
            "role": "user",
            "content": main_msg
        }]
        completion = self.llm.chat.completions.create(model=self.model, messages=msgs, temperature=self.temperature)
        return completion.choices[0].message.content if not self.reasoning_model else completion.choices[0].message.content.split("</think>")[1]



    def find_relation_json_text(self, relation: str):
        """Find the desired relation about the given, main key, extracted as a concise message in a json format"""
        relation_data = self.scraper.get_query_results_text(f"{self.key} {relation}")

        main_msg = f"""Extract the following data point: \"{relation}\", about the: \"{self.key}\"\n
                       From this pile of text:\n
                       {relation_data},
                       in the json format, as \"{self.key}\": {{
                           "{relation}": "answer"
                       }}.

                       Be as concise as possible, avoid any irrelevant data. Deliver only the asked data point ({relation}) or NULL in a json format.
                       Never include any explanation or anything besides the json.
                    """


        msgs = [
        {
            "role": "user",
            "content": main_msg
        }]
        completion = self.llm.chat.completions.create(model=self.model, messages=msgs, temperature=self.temperature)
        return completion.choices[0].message.content if not self.reasoning_model else completion.choices[0].message.content.split("</think>")[1]

    def find_relation_dictionary(self, relation: str):
        """
        Find the relation to the keyword and extract the data directly to a Python dictionary
        """
        json_text = self.find_relation_json_text(relation)
        json_match = re.search(r'```json\s*(.*?)\s*```', json_text, re.DOTALL)
        try:
            dictionary = json.loads(json_match.group(1))
        except:
            try:
                dictionary = json.loads(json_text)
            except:
                print(f"CRITICAL ERROR ({json_text})")
                dictionary = {}
        return dictionary

if __name__ == "__main__":
    test = RelationFinder("Anthropic PBC", model="phi4")
    print(test.find_verbose_relation("Competitor Analysis"))