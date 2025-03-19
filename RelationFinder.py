from SearchEngineScraper import SearchEngineScraper 
from openai import Client
import json
import re 


class RelationFinder:
    """
    Class used to perform searches on different relations between the main keyword and the relation
    """
    def __init__(self, keyword: str, base_url: str = "http://localhost:11434/v1", model: str="phi4", temperature: int = 0, reasoning_model=False):
        self.scraper = SearchEngineScraper()
        self.llm = Client(
                    base_url=base_url,
                    api_key="ollama"
        )
        self.key = keyword
        self.model = model
        self.temperature = temperature
        self.reasoning_model = reasoning_model

    def find_relation_json_text(self, relation: str):
        """Find the desired relation about the given, main key"""
        relation_data = self.scraper.get_query_results_text(f"{self.key} {relation}")
        msgs = [
        {
            "role": "user",
            "content": f"""Extract the following data point: \"{relation}\", about the: \"{self.key}\"\n
            From this pile of text:\n
            {relation_data},
            in the json format, as \"{self.key}\": {{
                "{relation}": "answer"
            }}.

            Be as concise as possible, avoid any irrelevant data. Deliver only the asked data point ({relation}) or null in a json format.
            Never include any explanation or anything besides the json.
            """
        }]
        completion = self.llm.chat.completions.create(model=self.model, messages=msgs, temperature=self.temperature)
        return completion.choices[0].message.content if not self.reasoning_model else completion.choices[0].message.content.split("</think>")[1]

    def find_relation_dictionary(self, relation: str):
        """
        Find the relation to the keyword and extract the data directly to a Python dictionary
        """
        json_text = self.find_relation_json_text(relation)
        json_match = re.search(r'```json\s*(.*?)\s*```', json_text, re.DOTALL)
        dictionary = json.loads(json_match.group(1))
        return dictionary

if __name__ == "__main__":
    test = RelationFinder("Cynexis Insight")
    print(test.find_relation_dictionary("Founders"))
    