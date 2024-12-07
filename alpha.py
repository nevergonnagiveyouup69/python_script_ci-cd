from googlesearch import search

def get_stock_ticker(company_name):
    query = f"{company_name} stock ticker"
    for result in search(query, num_results=5):
        if "finance" in result or "ticker" in result:
            print(result)
            break
        

get_stock_ticker("Brandbucket Media & Technology Ltd")
