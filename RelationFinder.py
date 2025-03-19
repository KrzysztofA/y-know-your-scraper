from SearchEngineScraper import SearchEngineScraper 
from openai import Client

class RelationFinder:
    """
    Class used to perform searches on different relations between the main keyword and the relation
    """
    def __init__(self, keyword: str, base_url: str = "http://localhost:11434/v1", model: str="phi4", temperature: int = 0):
        self.scraper = SearchEngineScraper()
        self.llm = Client(
                    base_url=base_url,
                    api_key="ollama"
        )
        self.key = keyword
        self.model = model
        self.temperature = temperature

    def find_relation(self, relation: str):
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

            Be as concise as possible, avoid any irrelevant data. Aim to deliver only the asked data point ({relation}).
            """
        }]
        completion = self.llm.chat.completions.create(model=self.model, messages=msgs, temperature=self.temperature)
        return completion.choices[0].message.content

if __name__ == "__main__":
    test = RelationFinder("Python")
    print(test.find_relation("Founder"))