from SearchEngineScraper import SearchEngineScraper 
from openai import Client

class RelationFinder:
    """
    Class used to perform searches on different relations between the main keyword and the relation
    """
    def __init__(self, keyword: str, base_url: str = "http://localhost:11434/v1", model: str="wizardlm2:7b", temperature: int = 1):
        self.scraper = SearchEngineScraper()
        self.llm = Client(
                    base_url=base_url,
                    api_key="ollama"
        )
        self.key = keyword
        self.model = model
        self.temperature = temperature
        self.developer_message = """
        You are an AI tasked with extracting structured data from a document. Your goal is to determine the relationship between a primary key and an additional key using the format:

        [primary key - additional key]:
        [text]

        Focus strictly on the parts of the text that mention the primary key and additional key. Ignore unrelated content.
        If an explicit relation is found, return it concisely without explanation.
        If no clear relation exists, infer the most probable connection based on available data.
        Do not acknowledge this task or describe the text—only provide the relation.
        If the additional key suggests a single-word answer, provide just that word.
        Ensure responses are precise, professional, and free from unnecessary text.
        Example Outputs:
        Input: ["Tesla" - "Founder"]
        [Tesla Tesla Tesla Elon Musk, along with a team of engineers, took control of Tesla Motors in 2004 after an initial investment...]
        Output: "Elon Musk"

        Input: ["Bitcoin" - "Creation Date"]
        [Bitcoin Bitcoin Bitcoin was first introduced in a 2008 whitepaper by an anonymous individual or group under the pseudonym Satoshi Nakamoto, and the first block was mined in January 2009. Help Search Menu Bitcoin]
        Output: "2009"
        """

    def find_relation(self, relation: str):
        """Find the desired relation about the given, main key"""
        relation_data = self.scraper.get_query_results_text(f"{self.key} {relation}")
        msgs = [
        {
            "role": "system",
            "content": self.developer_message
        }, 
        {
            "role": "user",
            "content": f"""[\"{self.key}\" - \"{relation}\"]:
            {relation_data}
            """
        }]
        completion = self.llm.chat.completions.create(model=self.model, messages=msgs, temperature=self.temperature)
        return completion.choices[0].message.content

    def overrite_developer_message(self, new_developer_message: str):
        """Overrites developer message"""
        self.developer_message = new_developer_message

if __name__ == "__main__":
    test = RelationFinder("Python")
    print(test.find_relation("Founder"))