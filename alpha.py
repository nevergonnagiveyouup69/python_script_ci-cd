from bs4 import BeautifulSoup
import requests
import random
import os
import re
import google.generativeai as genai
from googlesearch import search

def get_company_url(company_name):
    """
    Fetch the URL for the given company name from Finology.
    """
    query = f"{company_name} stock ticker"
    for result in search(query, num_results=5):
        if "finology" in result:

            response = requests.get(result)
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
            print(financial_data)
            print("profits:"+ profits)
            return profits, generated_text, financial_data
        
get_company_url("Brandbucket Media & Technology Ltd")
