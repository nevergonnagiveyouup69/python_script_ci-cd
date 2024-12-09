import yfinance as yf
from googlesearch import search
import re

def calculate_metrics(company_name):
    try:
        # Fetch stock data
        query = f"{company_name} stock ticker yahoo"
        for result in search(query, num_results=5):
            if "finance" in result or "yahoo" in result:
                match = re.search(r"/quote/([^/]+)/", result)
                ticker = match.group(1)
        print("ticker: "+ticker)
        stock = yf.Ticker(ticker)

        # Fetch financial data
        financials = stock.financials
        balance_sheet = stock.balance_sheet

        # Retrieve necessary values
        total_assets = balance_sheet.loc["Total Assets"].iloc[0]
        current_liabilities = balance_sheet.loc["Current Liabilities"].iloc[0]
        shareholder_equity = balance_sheet.loc["Stockholders Equity"].iloc[0]
        revenue = financials.loc["Total Revenue"].iloc[0]
        net_income = financials.loc["Net Income"].iloc[0]
        operating_income = financials.loc["Operating Income"].iloc[0]
        dividend_per_share = stock.info.get("dividendRate", 0)
        shares_outstanding = stock.info.get("sharesOutstanding", 1)
        market_price = stock.history(period="1d")["Close"].iloc[-1]
        total_shares = balance_sheet.loc["Ordinary Shares Number"].iloc[0]
        tangible_book_value = balance_sheet.loc["Tangible Book Value"].iloc[0]
        cash_balance = balance_sheet.loc["Cash And Cash Equivalents", :].iloc[0]
        income_statement = stock.financials
        balance_sheet = stock.balance_sheet

        # Extract required data
        ebit = income_statement.loc["EBIT"].iloc[0]
        total_assets = balance_sheet.loc["Total Assets"].iloc[0]

        # Calculate Capital Employed
        capital_employed = total_assets - current_liabilities

        # Fetch company info
        company_info = stock.info
        # Fetch insider and institutional holding percentages
        insider_holding = company_info.get('heldPercentInsiders', 'Data not available')
        institutional_holding = company_info.get('heldPercentInstitutions', 'Data not available')


        # Calculations
        book_value_per_share = tangible_book_value / total_shares
        pb_ratio = market_price / book_value_per_share
        pe_ratio = stock.info.get("trailingPE", "N/A")
        roa = (net_income / total_assets) * 100 if total_assets else "N/A"
        current_ratio = total_assets / current_liabilities if current_liabilities else "N/A"
        roe = (net_income / shareholder_equity) * 100 if shareholder_equity else "N/A"
        debt_equity = balance_sheet.loc["Total Debt"].iloc[0] / balance_sheet.loc["Tangible Book Value"].iloc[0]
        operating_margin = (operating_income / revenue) * 100 if revenue else "N/A"
        eps = net_income / shares_outstanding if shares_outstanding else "N/A"
        dividend_yield = (dividend_per_share / market_price) * 100 if market_price else "N/A"

        # Sales Growth and other data (using additional data if available)
        revenue_last_year = financials.loc["Total Revenue"].iloc[1] if len(financials.columns) > 1 else 0
        sales_growth = ((revenue - revenue_last_year) / revenue_last_year) * 100 if revenue_last_year else "N/A"
        roce = (ebit / capital_employed) * 100

        # Compile data
        fundamental_data = {
            "Sector": stock.info.get("sector"),
            "Industry": stock.info.get("industry"),
            "market price": float(round(market_price, 2)),
            "Market Cap": float(stock.info.get("marketCap", 0)),
            "P/E": float(round(pe_ratio, 2)),
            "Return on Assets (ROA)": float(round(roa, 2)),
            "Current Ratio": float(round(current_ratio, 2)),
            "ROE": float(round(roe, 2)),
            "Debt": float(round(debt_equity, 3)),
            "Operating Margin": float(round(operating_margin, 2)),
            "Dividend Yield": float(round(dividend_yield, 2)),
            "Earnings Per Share (EPS)": float(round(eps, 2)),
            "Sales": float(round(sales_growth, 2)),
            "52-Week High": float(stock.info.get("fiftyTwoWeekHigh", 0)),
            "52-Week Low": float(stock.info.get("fiftyTwoWeekLow", 0)),
            "Revenue": float(revenue),
            "Net Income": float(net_income),
            "Total Assets": float(total_assets),
            "P/B": float(round(pb_ratio, 2)),
            "ROCE": float(round(roce)),
            "Institutional Holding": float(round(institutional_holding*100)),
            "Promoter Holding":float(round(insider_holding*100)),
            "Cash":float(cash_balance)
        }
        return fundamental_data
    except Exception as e:
        print(f"Error fetching fundamental data for {ticker}: {e}")
        return None