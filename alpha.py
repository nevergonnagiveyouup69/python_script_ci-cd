from bs4 import BeautifulSoup
import requests
# Example: Using requests to fetch the HTML content (you can replace this with your HTML content directly)  
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
import random
import os
import re
import google.generativeai as genai
from playwright_stealth import stealth_sync



# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from nltk.metrics import edit_distance

value = "D P Abhushan Ltd"

def get_company_url(value):
   
    """
    Fetch the URL for the given company name from Finology.
    """
    try:
        with sync_playwright() as p:

            # Launch the browser
            browser = playwright.chromium.launch(headless=False)
            context = browser.new_context()
            stealth_sync(context)
            page = context.new_page()
            print("Starting server")
            page = browser.new_page()

            # Ticker list and preprocessing
            ticker = ['RELIANCE', 'ITC', 'tcs', 'wipro', 'hcltech', 'TECHM', 'INFY', 'OFSS', 
                    'HDFCBANK', 'ICICIBANK', 'YESBANK', 'ntpc', 'TATAPOWER', 'ongc']
            value = "Brandbucket Media & Technology Ltd."
            value = re.sub(r'\blimited\b', 'ltd', value, flags=re.IGNORECASE)
            value = re.sub(r'\band\b', '&', value, flags=re.IGNORECASE)
            print("Value (Stock name):", value)
            
            # Select a random ticker
            random_ticker = random.choice(ticker)
            print("Randomly selected ticker:", random_ticker)
            
            # Navigate to the page
            page.goto(f"https://ticker.finology.in/company/{random_ticker}")

            # Wait for the search box and interact
            try:
                page.wait_for_selector('[class="topsearchinner"]', timeout=30000)
                page.locator('[class="topsearchinner"]').click()
                page.locator('[id="txtSearchComp"]').type(value, delay=100)
                
                # Wait for dropdown and select
                page.wait_for_selector('[class="list animated fadeInUp faster"]', timeout=30000)
                page.locator('[class="list animated fadeInUp faster"]').nth(0).click()
                
                # Get the base URL after interaction
                base_url = page.url
                print("Extraction successful. Server URL:", base_url)

            except Exception as e:
                print("Error occurred during element interaction:", str(e))
                # Save a screenshot and page content for debugging
                os.makedirs("debug", exist_ok=True)  # Ensure the debug folder exists
                screenshot_path = os.path.join("debug", "error_screenshot.png")
                html_path = os.path.join("debug", "error_page.html")
                
                page.screenshot(path=screenshot_path)
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(page.content())
                
                print(f"Screenshot saved at: {screenshot_path}")
                print(f"HTML dump saved at: {html_path}")
                financial_data = {
                "Market Cap":"0",
                "Enterprise Value":"0",
                "Number of Shares":"0",
                "P/E":"0",
                "P/B":"0",
                "Dividend Yield":"0",
                "Cash":"0",
                "Debt":"0",
                "Promoter Holding": "0",
                "Sales": "0",
                "ROE": "0",
                "ROCE": "0",
                }
                print(f"The playwright couldn't find anything, likely because the data isn't available. If it's waiting for a locator, that might be the issue:{e}")
                return "no data", "no data", financial_data
            browser.close()

    except Exception as e:
        print("Error occurred:", str(e))

    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print("\nStarting extraction:")
    # Find all list items within the content
   
    # Assuming 'soup' is your BeautifulSoup object
    list_items = soup.find_all("li")
    reports_found = False  # Flag to start capturing items after the reports
    
    after_reports_items = []  # List to store filtered items

    # Define a list of keywords to exclude
    exclude_keywords = [
        "CreditReport", "Research", "Concall", "Presentation"
    ]
    # Iterate through the list items
    for item in list_items:
        # Check if the item is an annual report
        if "Annual Report" in str(item):
            reports_found = True
            continue

        # If reports have been found, start processing
        if reports_found:
            text = item.get_text(strip=True)
            # Check if the text contains any of the exclude keywords
            if not any(keyword in text for keyword in exclude_keywords):
                # Apply the regex to each item in after_reports_items
                after_reports_items.append(text)

    def extract_financial_value(index):
        value = soup.find_all('div', {'class': 'col-6 col-md-4 compess'})
        return value[index].find('p').text.strip() if len(value) > index else "N/A"
    

   # Extract P/E, P/B, Div Yield, Cash, Debt, Promoter Holding, Sales, ROE, ROCE
    financial_data = {
        "Market Cap": extract_financial_value(0) or "0",
        "Enterprise Value": extract_financial_value(1) or "0",
        "Number of Shares": extract_financial_value(2) or "0",
        "P/E": extract_financial_value(3) or "0",
        "P/B": extract_financial_value(4) or "0",
        "Dividend Yield": re.sub(r"\s+", " ", extract_financial_value(6)).strip() or "0",
        "Cash": extract_financial_value(8) or "0",
        "Debt": extract_financial_value(9) or "0",
        "Promoter Holding": extract_financial_value(10) or "0",
        "Sales": extract_financial_value(12) or "0",
        "ROE": extract_financial_value(13) or "0",
        "ROCE": extract_financial_value(14) or "0",
    }

    
    genai.configure(api_key=os.getenv('API_KEY_GEN_2'))
    model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"temperature": 0.2})
    response = model.generate_content("I want you to analyze the data and provide a financial analysis (profitability) of this in single paragraph no highlights"+str(after_reports_items)+"fundamentals"+str(financial_data))
    generated_text = response.text
    
    # original_data = str(after_reports_items)+str(financial_data)
    
    # vectorizer = CountVectorizer().fit_transform([original_data, generated_text])
    # vectors = vectorizer.toarray()

    # def jaccard_similarity(text1, text2):
    #     set1, set2 = set(text1.split()), set(text2.split())
    #     intersection = set1.intersection(set2)
    #     union = set1.union(set2)
    #     return len(intersection) / len(union)

    # distance = edit_distance(original_data, generated_text)
    # print("")
    # print("Edit Distance:", distance)

    # similarity = jaccard_similarity(original_data, generated_text)
    # print("Jaccard Similarity:", similarity)

    # cos_sim = cosine_similarity(vectors)
    # print("Cosine Similarity:", cos_sim[0, 1])
    # print("")
    # print("the output:"+generated_text)

    model2 = genai.GenerativeModel("gemini-1.5-flash")
    response2 = model2.generate_content("Summarize the profitability of this investment in one word: 'Low,' 'Moderate,' 'High,' 'Very High,' or 'None'."+str(after_reports_items)+"fundamentals"+str(financial_data))
    profits = response2.text
    print("Extraction Completed.\n")
    # print(financial_data)
    # print("profits:"+ profits)
    return profits, generated_text, financial_data

get_company_url(value)