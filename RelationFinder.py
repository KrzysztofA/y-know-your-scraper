from SearchEngineScraper import SearchEngineScraper
from nltk.tokenize import word_tokenize
import nltk
from openai import Client
import json
import re 
from typing import List


class RelationFinder:
    """
    Class used to perform searches on different relations between the main keyword and the relation
    """
    def __init__(self, keyword: str, base_url: str = "http://localhost:11434/v1", model: str="phi4", temperature: int = 0.1, api_key:str="ollama", reasoning_model=False):
        self.scraper = SearchEngineScraper()
        self.llm = Client(
                    base_url=base_url,
                    api_key=api_key
        )
        self.key = keyword
        self.model = model
        self.temperature = temperature
        self.reasoning_model = reasoning_model

    def __send_chat_message(self, main_msg: str):
        """Send a user message to the chat with LLM"""
        msgs = [
        {
            "role": "user",
            "content": main_msg
        }]
        completion = self.llm.chat.completions.create(model=self.model, messages=msgs, temperature=self.temperature)
        return completion

    def __summarize_text(self, text: str):
        """Levreges LLMs to provide a summary of a given text"""
        main_msg = f"""
        Provide a concise summary of the given text, ignore sentences making no sense or singular words out of context:\n
        {text}\n\n

        Make your answer provides only the summary, no acknowledgements of the task, no preambles.
        """
        completion = self.__send_chat_message(main_msg)
        return completion.choices[0].message.content if not self.reasoning_model else completion.choices[0].message.content.split("</think>")[1]
    
    def __tokenize_text(self, text: str):
        """Tokenize given text and return the number of tokens"""
        return len(word_tokenize(text))
    
    def __reduce_text(self, text: str, max_tokens: int):
        """Reduce text so it contains a maximum number of tokens"""
        # TODO remove recursion and try to make a list        
        if self.__tokenize_text(text) < max_tokens:
            return text

        # Split text into individual sentences
        sentences_list = text.split(".")
        sentences_list = [a.strip() for a in sentences_list]
        desired_text = sentences_list[0]
        temp_desired_text = desired_text
        full_text = ""

        # For the whole length of the text, reduce it to a maximum number of tokens
        while index != len(sentences_list):

            # Get the text up to a given number of max tokens
            index = 1
            while(self.__tokenize_text(temp_desired_text) < max_tokens and index < len(sentences_list)):
                desired_text = temp_desired_text
                index += 1
                temp_desired_text += "." + sentences_list[index]

            if index != len(sentences_list):
                index -= 1
            
            desired_text = desired_text.strip()
            desired_text += "."

            # Summarize the gathered text 
            full_text += self.__summarize_text(desired_text)

        # If the text is still too large, repeat the process
        if self.__tokenize_text(full_text) > max_tokens:
            return self.__reduce_text(full_text, max_tokens)
        return full_text

    def __parse_articles_to_summary(self, articles: List, max_tokens: int):
        """Parses each article to be reduced to a short summary."""
        for article in articles:
            article = self.__reduce_text(article, max_tokens)
        if self.__tokenize_text("\n\n".join(articles)) > max_tokens:
            return self.__parse_articles_to_summary(articles, max_tokens)
        return articles

    def __get_data(self, relation: str, reduce: bool = False, max_tokens: int = -1):
        """Gets the data for the relation"""
        relation_data = self.scraper.get_query_results_text(f"{self.key} {relation}")
        if reduce:
            relation_data = self.__parse_articles_to_summary(relation_data, max_tokens)
        return relation_data

    def find_verbose_relation(self, relation: str, reduce: bool = False, max_tokens: int = -1):
        """Find desired relation about the given main key, and build an article explaining the relation"""
        relation_data = self.__get_data(relation, reduce, max_tokens)
        main_msg = f"""Extract the following data point: \"{relation}\", about the: \"{self.key}\"\n
                       From this pile of text:\n
                       {relation_data},
                       prepare a verbose and detailed article on \"{relation}\" for a business report with as many details as you can find in the given text about the \"{self.key}.
                       Make sure the article is professional. Don't include any preambles, nor any acknowledgements or anything besides the article.
                    """
        completion = self.__send_chat_message(main_msg)
        return completion.choices[0].message.content if not self.reasoning_model else completion.choices[0].message.content.split("</think>")[1]

    def find_relation_json_text(self, relation: str, reduce: bool = False, max_tokens: int = -1):
        """Find the desired relation about the given, main key, extracted as a concise message in a json format"""
        relation_data = self.__get_data(relation, reduce, max_tokens)

        main_msg = f"""Extract the following data point: \"{relation}\", about the: \"{self.key}\"\n
                       From this pile of text:\n
                       {relation_data},
                       in the json format, as \"{self.key}\": {{
                           "{relation}": "{relation} relation to {self.key}"
                       }}.

                       Be as concise as possible, avoid any irrelevant data. Deliver only the asked data point ({relation}) or NULL in a json format.
                       Never include any explanation or anything besides the json.
                    """
        completion = self.__send_chat_message(main_msg)
        return completion.choices[0].message.content if not self.reasoning_model else completion.choices[0].message.content.split("</think>")[1]

    def find_relation_dictionary(self, relation: str, reduce: bool = False, max_tokens: int = -1):
        """
        Find the relation to the keyword and extract the data directly to a Python dictionary
        """
        json_text = self.find_relation_json_text(relation, reduce, max_tokens)
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
    # nltk.download() # Only run this on the first run, and then comment it out
    test = RelationFinder("Anthropic PBC", model="llama2")
    print(test.find_relation_dictionary("Known Competitors", True, 10000))