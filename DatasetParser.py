import pandas as pd
from RelationFinder import RelationFinder

class DatasetParser:
    """
    Class responsible for parsing the dataset
    """
    def __init__(self, file_path: str):
        self.data = pd.read_csv(file_path)

    def fill_missing_data_with_ai_at_index(self, index:int, model="phi4"):
        """
        Fills the missing data using provided llm and appends this data to the given CSV TODO
        """
        
        # Extract company
        company = self.data.iloc[index, 0]
        
        # Create relationship finder instance
        company_relation_finder = RelationFinder(company, model=model)
        
        # Enumerate values from the given row
        for i, val in enumerate(self.data.iloc[index, 1:]):
            
            # Find null values and attempt to fill them with LLM
            if pd.isnull(val):
                column = self.data.columns[i+1]
                print(f"Starting scraping null value {column} at index {i} for company {company}")
                data_scraped = company_relation_finder.find_relation_dictionary(column)
                null_data = data_scraped[company][column]
                print(null_data)


if __name__ == "__main__":
    data_parser = DatasetParser("knowYourAi - Company Details.csv")
    data_parser.fill_missing_data_with_ai_at_index(1)