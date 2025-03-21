import pandas as pd
from RelationFinder import RelationFinder

class DatasetAIParser:
    """
    Class responsible for parsing the dataset
    """
    def __init__(self, file_path: str):
        self.data = pd.read_csv(file_path)
        self.file_path = file_path

    def fill_missing_data_with_ai_at_index(self, index:int, model="phi4", max_tokens: int = 10000):
        """
        Fills the missing data using provided llm and appends this data to the given CSV TODO
        """
        
        # Extract company
        company = self.data.iloc[index, 0]
        
        # Create relationship finder instance
        company_relation_finder = RelationFinder(company, model=model)
        
        # Enumerate values from the given row
        for i, val in enumerate(self.data.iloc[index, 1:30]):
            
            # Find null values and attempt to fill them with LLM
            if pd.isnull(val):
                try:
                    column = self.data.columns[i + 1]
                    print(f"Starting scraping null value {column} at index {i} for a company {company}")
                    data_scraped = company_relation_finder.find_relation_dictionary(column, True, max_tokens)
                    null_data = data_scraped[company][column]
                    self.data.iloc[index, i+1] = self.data.iloc[index, i+1].astype(str)
                    self.data.iloc[index, i+1] = str(null_data)
                    print(f"Data obtained: {null_data}")
                except:
                    print("Error occured, continuing to the next field")
                    continue

    def finish_operations(self):
        new_file_path = self.file_path.replace(".csv", " - AI Modified.csv")
        self.data.to_csv(new_file_path)


if __name__ == "__main__":
    data_parser = DatasetAIParser("knowYourAi - Company Details.csv")
    data_parser.fill_missing_data_with_ai_at_index(0, model="llama2")
    data_parser.finish_operations()