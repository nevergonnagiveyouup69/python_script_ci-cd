
import time
import google.generativeai as genai # type: ignore
from finance import calculate_metrics
import os

def profits_chance(financial_data):
        genai.configure(api_key=os.getenv('API_KEY_GEN_3'))
        model2 = genai.GenerativeModel("gemini-1.5-flash")
        response2 = model2.generate_content("Summarize the profitability of this investment in one word: 'Low,' 'Moderate,' 'High,' 'Very High,' or 'None'.fundamentals"+str(financial_data))
        profits = response2.text
        return profits


def get_company_url(company_name):
        max_retries = 5  # Maximum number of retries
        retry_wait = 60  # Wait time in seconds (1 minute)

        for attempt in range(max_retries):
                try:
                        financial_data = calculate_metrics(company_name)
                        genai.configure(api_key=os.getenv('API_KEY_GEN_2'))
                        model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"temperature": 0.2})
                        response = model.generate_content("I want you to analyze the data and provide a financial analysis (profitability) of this in single paragraph no highlights fundamentals"+str(financial_data))
                        generated_text = response.text
                        profits = profits_chance(financial_data)
                        print("Extraction Completed.\n")
                        print(financial_data)
                        # print("profits:"+ profits)
                        return profits, generated_text, financial_data
                        
                except google.api_core.exceptions.ResourceExhausted as e:
                        print(f"Resource exhausted: {e}. Retrying in {retry_wait} seconds... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_wait)  # Wait for 1 minute before retrying

                except Exception as e:
                        print(f"An unexpected error occurred: {e}")
                        break  # Exit loop for non-retryable errors

        print("All retry attempts failed. Please check your quota or try again later.")
        return None
