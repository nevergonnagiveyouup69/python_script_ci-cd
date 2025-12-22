import google.genai as genai
import os
import time
import random
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(5))
def profits_chance(financial_data):
    try:
        client = genai.Client(api_key=os.getenv("API_KEY_GEN"))

        # Prepare your prompt text
        prompt = (
            "Summarize the profitability of this investment in one word: "
            "'Low,' 'Moderate,' 'High,' 'Very High,' or 'None'.\n\n"
            f"Fundamentals: {financial_data}"
        )

        # Call the Gemini model (choose an available text model, e.g., gemini-2.5-flash)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # Extract plain text response
        profits = response.text.strip() if response.text else "Moderate"
        return profits
   
    except Exception as e:
        # Retry if rate limited
        if "429" in str(e):
            print(f"Rate limit hit, retrying... ({e})")
            time.sleep(random.uniform(1, 3))
            raise e  # Trigger retry via decorator
        else:
            print(f"Error in profits_chance: {e}")
            return "Moderate"  # Safe fallback