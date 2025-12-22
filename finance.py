import yfinance as yf # type: ignore
from googlesearch import search # type: ignore
import re

def calculate_metrics(company_name):
    ticker = None
    try:
        # Fetch stock data
        query = f"{company_name} stock ticker yahoo"
        for result in search(query, num_results=5):
            if "finance" in result or "yahoo" in result:
                match = re.search(r"/quote/([^/]+)/", result)
                if match:
                    ticker = match.group(1)
                    break
                else:
                    raise ValueError(f"No valid ticker found for company {company_name}")
        if not ticker:
            raise ValueError(f"No valid ticker found for company {company_name}")
        stock = yf.Ticker(ticker)

        # Fetch financial data
        financials = stock.financials
        balance_sheet = stock.balance_sheet

        # Retrieve necessary values
        total_assets = balance_sheet.loc["Total Assets"].iloc[0] if "Total Assets" in balance_sheet.index else 0
        current_liabilities = balance_sheet.loc["Current Liabilities"].iloc[0] if "Current Liabilities" in balance_sheet.index else 0
        shareholder_equity = balance_sheet.loc["Stockholders Equity"].iloc[0] if "Stockholders Equity" in balance_sheet.index else 0    
        revenue = financials.loc["Total Revenue"].iloc[0] if "Total Revenue" in financials.index else 0
        net_income = financials.loc["Net Income"].iloc[0] if "Net Income" in financials.index else 0
        operating_income = financials.loc["Operating Income"].iloc[0] if "Operating Income" in financials.index else 0
        dividend_per_share = stock.info.get("dividendRate", 0) 
        shares_outstanding = stock.info.get("sharesOutstanding", 1)
        market_price = stock.history(period="1d")["Close"].iloc[-1]
        total_shares = balance_sheet.loc["Ordinary Shares Number"].iloc[0] if "Ordinary Shares Number" in balance_sheet.index else 0
        tangible_book_value = balance_sheet.loc["Tangible Book Value"].iloc[0] if "Tangible Book Value" in balance_sheet.index else 0
        cash_balance = balance_sheet.loc["Cash And Cash Equivalents", :].iloc[0] if "Cash And Cash Equivalents" in balance_sheet.index else 0
        income_statement = stock.financials
        balance_sheet = stock.balance_sheet

        # Extract required data
        ebit = income_statement.loc["EBIT"].iloc[0] if "EBIT" in income_statement.index else 0
        total_assets = balance_sheet.loc["Total Assets"].iloc[0] if "Total Assets" in balance_sheet.index else 0

        # Calculate Capital Employed
        capital_employed = total_assets - current_liabilities

        # Fetch company info
        company_info = stock.info
        # Fetch insider and institutional holding percentages
        insider_holding = company_info.get('heldPercentInsiders', 'Data not available')
        institutional_holding = company_info.get('heldPercentInstitutions', 'Data not available')


        # Calculations
        # Ensure no division by zero errors
        book_value_per_share = tangible_book_value / total_shares if total_shares else "N/A"
        pb_ratio = market_price / book_value_per_share if book_value_per_share != "N/A" else "N/A"
        pe_ratio = stock.info.get("trailingPE", "N/A")
        roa = (net_income / total_assets) * 100 if total_assets else "N/A"
        current_ratio = total_assets / current_liabilities if current_liabilities else "N/A"
        roe = (net_income / shareholder_equity) * 100 if shareholder_equity else "N/A"
        debt_equity = (
            balance_sheet.loc["Total Debt"].iloc[0] / tangible_book_value
            if tangible_book_value else "N/A"
        )
        operating_margin = (operating_income / revenue) * 100 if revenue else "N/A"
        eps = net_income / shares_outstanding if shares_outstanding else "N/A"
        dividend_yield = (dividend_per_share / market_price) * 100 if market_price else "N/A"

        # Handle sales growth calculation
        revenue_last_year = financials.loc["Total Revenue"].iloc[1] if len(financials.columns) > 1 else 0
        sales_growth = (
            ((revenue - revenue_last_year) / revenue_last_year) * 100
            if revenue_last_year else "N/A"
        )

        # ROCE calculation
        roce = (ebit / capital_employed) * 100 if capital_employed else "N/A"

        def safe_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0
            
        # Compile data
        fundamental_data = {
            "Sector": stock.info.get("sector"),
            "Industry": stock.info.get("industry"),
            "market price": safe_float(round(market_price, 2)),
            "Market Cap": safe_float(stock.info.get("marketCap", 0)),
            "P/E": safe_float(round(pe_ratio, 2)) if pe_ratio != "N/A" else "N/A",
            "Return on Assets (ROA)": safe_float(round(roa, 2)) if roa != "N/A" else "N/A",
            "Current Ratio": safe_float(round(current_ratio, 2)) if current_ratio != "N/A" else "N/A",
            "ROE": safe_float(round(roe, 2)) if roe != "N/A" else "N/A",
            "Debt": safe_float(round(debt_equity, 3)) if debt_equity != "N/A" else "N/A",
            "Operating Margin": safe_float(round(operating_margin, 2)) if operating_margin != "N/A" else "N/A",
            "Dividend Yield": safe_float(round(dividend_yield, 2)) if dividend_yield != "N/A" else "N/A",
            "Earnings Per Share (EPS)": safe_float(round(eps, 2)) if eps != "N/A" else "N/A",
            "Sales": safe_float(round(sales_growth, 2)) if sales_growth != "N/A" else "N/A",
            "52-Week High": safe_float(stock.info.get("fiftyTwoWeekHigh", 0)),
            "52-Week Low": safe_float(stock.info.get("fiftyTwoWeekLow", 0)),
            "Revenue": safe_float(revenue),
            "Net Income": safe_float(net_income),
            "Total Assets": safe_float(total_assets),
            "P/B": safe_float(round(pb_ratio, 2)) if pb_ratio != "N/A" else "N/A",
            "ROCE": safe_float(round(roce, 2)) if roce != "N/A" else "N/A",
            "Institutional Holding": safe_float(round(institutional_holding * 100, 2)) if institutional_holding != "Data not available" else "N/A",
            "Promoter Holding": safe_float(round(insider_holding * 100, 2)) if insider_holding != "Data not available" else "N/A",
            "Cash": safe_float(cash_balance),
        }
        print(fundamental_data)
        return fundamental_data
    except Exception as e:
        print(f"Error fetching fundamental data for {ticker}: {e}")
        return None
    