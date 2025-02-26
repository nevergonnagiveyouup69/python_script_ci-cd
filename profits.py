import google.generativeai as genai
import os
import time
import random
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(5))
def profits_chance(financial_data):
    try:
        genai.configure(api_key=os.getenv('API_KEY_GEN'))
        model = genai.GenerativeModel("gemini-1.5-flash")
        response2 = model.generate_content("Summarize the profitability of this investment in one word: 'Low,' 'Moderate,' 'High,' 'Very High,' or 'None'.fundamentals:"+str(financial_data))
        profits = response2.text
        return profits
    except Exception as e:
        if "429" in str(e):  # Rate limit error
            print(f"Rate limit hit, retrying... ({e})")
            time.sleep(random.uniform(1, 3))  # Add jitter
            raise e  # Retry via decorator
        else:
            print(f"Error in profits_chance: {e}")
            return "Moderate"  # Default fallback