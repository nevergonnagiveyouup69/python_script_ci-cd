from profits import profits_chance
import time
import os

# Correct import for the new SDK
from google import genai  # type: ignore

from finance import calculate_metrics

def get_company_url(company_name):
    max_retries = 5
    retry_wait = 60  # seconds

    # Initialize GenAI client once (reuse connection)
    client = genai.Client(api_key=os.getenv("API_KEY_GEN_2"))

    for attempt in range(max_retries):
        try:
            # Calculate financial metrics
            financial_data = calculate_metrics(company_name)

            # Prompt for full financial analysis
            prompt = (
                "I want you to analyze the data and provide a financial analysis "
                "(profitability) of this in a single paragraph with fundamentals: "
                f"{financial_data}"
            )

            # Call the Gemini text model
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            generated_text = response.text.strip()

            # Get the profitability word (Low/Moderate/High/etc.)
            profits = profits_chance(financial_data)

            print("Extraction Completed. \n")
            print(financial_data)

            return profits, generated_text, financial_data

        except Exception as e:
            # If it's a rate limit or quota error, wait and retry
            if "429" in str(e) or "ResourceExhausted" in str(e):
                print(
                    f"Rate limit / resource exhausted: {e}. "
                    f"Retrying in {retry_wait}s... ({attempt + 1}/{max_retries})"
                )
                time.sleep(retry_wait)
                continue
            # For other errors, break out
            print(f"An unexpected error occurred: {e}")
            break

    print("All retry attempts failed. Please check your quota or try later.")
    return None
