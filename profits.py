import google.generativeai as genai # type: ignore
import os

def profits_chance(financial_data):
        genai.configure(api_key=os.getenv('API_KEY_GEN_3'))
        model2 = genai.GenerativeModel("gemini-1.5-flash")
        response2 = model2.generate_content("Summarize the profitability of this investment in one word: 'Low,' 'Moderate,' 'High,' 'Very High,' or 'None'.fundamentals"+str(financial_data))
        profits = response2.text
        return profits