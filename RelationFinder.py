from SearchEngineScraper import SearchEngineScraper 
from openai import Client

class RelationFinder:
    """
    Class used to perform searches on different relations between the main keyword and the relation
    """
    def __init__(self, keyword: str, localhost: str = "11434", model: str="deepseek-r1", precision: int = 1):
        self.scraper = SearchEngineScraper()
        self.llm = Client(
                    base_url=f"http://localhost:{localhost}/v1",
                    api_key="ollama"
        )
        self.key = keyword
        self.model = model
        self.precision = precision
        self.developer_message = """
        You are a helpful assistant that is tasked with finding data about the relation between the key and an additional key from a text in a format: 
        [key - additional key]:
        ""long, relevant text""

        The long, relevant text may be structured as a HTML file, look only at the relevant parts to the key and the additional key.
        If you cannot find the relation, provide the most probable estimate.
        When structuring your response:
        - be as concise as possible
        - avoid ackowledgements of the task
        - be professional
        - if the additional key indicates it requires only a single word to be answered, make the response a single word
        - avoid friendly chitchat
        """

    def find_relation(self, relation: str):
        """Find the desired relation about the given, main key"""
        relation_data = self.scraper.get_query_results_text(f"{self.key} {relation}")
        msgs = [{
            "role": "developer",
            "content": self.developer_message
        }, 
        {
            "role": "user",
            "content": f"""
            [{self.key} - {relation}]
            \"\"{relation_data}\"\"
            """
        }]

        completion = self.llm.chat.completions.create(model=self.model, messages=msgs, temperature=self.precision)
        return completion

    def overrite_developer_message(self, new_developer_message: str):
        """Overrites developer message"""
        self.developer_message = new_developer_message

if __name__ == "__main__":
    test = RelationFinder("Python")
    print(test.find_relation("Github Repositories Using").choices[0].message)