
import google.generativeai as genai
from finance import calculate_metrics

def get_company_url(company_name):
        
        financial_data = calculate_metrics(company_name)
        genai.configure(api_key=os.getenv('API_KEY_GEN_2'))
        model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"temperature": 0.2})
        response = model.generate_content("I want you to analyze the data and provide a financial analysis (profitability) of this in single paragraph no highlights fundamentals"+str(financial_data))
        generated_text = response.text
        
        
        model2 = genai.GenerativeModel("gemini-1.5-flash")
        response2 = model2.generate_content("Summarize the profitability of this investment in one word: 'Low,' 'Moderate,' 'High,' 'Very High,' or 'None'.fundamentals"+str(financial_data))
        profits = response2.text
        print("Extraction Completed.\n")
        print(financial_data)
        # print("profits:"+ profits)
        return profits, generated_text, financial_data
