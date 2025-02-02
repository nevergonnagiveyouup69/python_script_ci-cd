import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup 
from email.mime.base import MIMEBase
from email import encoders

# script.py
def some_function():
    from fetch import make_pdf
    make_pdf()

from dotenv import load_dotenv

def fetch_data():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        url = "https://trendlyne.com/equity/group-insider-trading-sast/"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        val = response.text

        soup = BeautifulSoup(val, "html.parser")

        table_header = soup.find("thead")
        headers = []

        if table_header:
            th_elements = table_header.find_all("th")
            headers = [th.text.strip() for th in th_elements]
        else:
            first_row = soup.find("tr")
            if first_row:
                th_elements = first_row.find_all("th")
                headers = [th.text.strip() for th in th_elements]

        patterns = {
            'Stock': r"\b(Stock|Ticker|Company)\w*\b",
            'AvgPrice': r"\b(Avg|Average)\b.*\bPrice\b",
            'Client': r"\bClient\b.*\b(Name|Category)\b",
            'Quantity': r"\b(Quantity|Qty)\w*\b",
            'Action': r"\bAction\*?\b",
            'ReportedToExchange': r"\bReported\b.*\bExchange\b",
            'PostTransactionHolding': r"\bPost\b.*\bTransaction\b.*\bHolding\b",
            'TradedPercent': r"\s*[tra](trade|de|ed|ding).*\s*[%]*\s*",
            'Value': r"\bValue\b",
            'Period': r"\bPeriod\b",
            'Regulation': r"\bRegulation\b.*\b(Insider|SAST)\b",
            'SecurityType': r"\bSecurity\sType\b" 
        }

        matched_headers = {}
        for key, pattern in patterns.items():
            for i, header in enumerate(headers):
                if re.search(pattern, header):
                    matched_headers[key] = (i, header)

        table_rows = soup.find_all("tr")
        extracted_data = []

        for row in table_rows:
            td_elements = row.find_all("td")
            if len(td_elements) >= 14:
                if (td_elements[matched_headers['Regulation'][0]].get_text() != 'Insider Trading') and (td_elements[matched_headers['SecurityType'][0]].get_text() == 'Equity Shares') and (td_elements[matched_headers['Action'][0]].get_text() == 'Acquisition') and (int(td_elements[matched_headers['Quantity'][0]].get_text().replace(",", "")) > 100000):
                    data = {
                        "Company Name": td_elements[matched_headers['Stock'][0]].find("a").text.strip(),
                        "Date": td_elements[matched_headers['Period'][0]].text.strip(),
                        "Quantity": td_elements[matched_headers['Quantity'][0]].text.strip(),
                        "Price": td_elements[matched_headers['AvgPrice'][0]].text.replace(' ', '').replace('\n', ' ').strip(),
                        "Percentage Change": td_elements[matched_headers['TradedPercent'][0]].text.replace(' ', '').replace('\n', ' ').strip(),
                        "Action": td_elements[matched_headers['Action'][0]].text.strip(),
                        "Value": td_elements[matched_headers['Value'][0]].text.strip(),
                    }
                    extracted_data.append(data)

        return extracted_data

    except requests.exceptions.RequestException as e:
        print(f"Error while fetching the URL: {e}")
        return None

def fetch_data_ipo():
    try:
        # Define the headers and URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        url = "https://www.investorgain.com/report/live-ipo-gmp/331/ipo/"

        # Send the GET request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if request was successful

        # Parse the response content
        soup = BeautifulSoup(response.text, "html.parser")

        table_header = soup.find("thead")
        headers = []

        if table_header:
            th_elements = table_header.find_all("th")
            headers = [th.text.strip() for th in th_elements]
        else:
            first_row = soup.find("tr")
            if first_row:
                th_elements = first_row.find_all("th")
                headers = [th.text.strip() for th in th_elements]

        # Find the table
        table = soup.find("table", {"id": "mainTable"})  # Adjust if a different attribute is needed
        if not table:
            print("Table not found on the page.")
            exit()

        # Extract data from table rows and columns
        extracted_data = []
        rows = table.find_all("tr")
        
        # Skip the header row if it exists
        for row in rows[1:]:  # Start from 1 to skip the header
            cols = row.find_all("td")
            if len(cols) > 1:  # Skip empty rows if they exist
                company_name = re.sub(r'Open\s*\(', ' Open (', re.sub(r'IPOUpcoming', 'IPO Upcoming',cols[0].text.strip().replace('[email\xa0protected]', '')))
        
                # Extract the percentage value within parentheses
                match = re.sub(r'--','0',re.sub(r'.*\d*\s\(', '', re.sub(r'%*\s*\)', '',cols[3].text.strip())))
                if round(float(match)) > 1:

                    if "Open" in company_name or "Upcoming" in company_name:
                        entry = {
                            "Company Name": company_name,
                            "Price":cols[1].text.strip(),
                            "GMP": cols[2].text.strip(),
                            "Est Listing": cols[3].text.strip(),
                            "IPO Size": cols[5].text.strip(),
                            "Lot": cols[6].text.strip()
                        }
                        extracted_data.append(entry)

        # Print the extracted data
        return extracted_data

    except requests.exceptions.RequestException as e:
        print(f"Error while fetching the URL: {e}")
        return None


def create_html_table(data):
    if not data:
        html = "<p>Something went wrong please check the code.</p>"
        return html
    
    html = '<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">'
    html += '<tr><th>Company Name</th><th>Date</th><th>Quantity</th><th>Price</th><th>Percentage Change</th><th>Action</th><th>Value</th></tr>'
    
    for item in data:
        html += '<tr>'
        html += f'<td>{item["Company Name"]}</td>'
        html += f'<td>{item["Date"]}</td>'
        html += f'<td>{item["Quantity"]}</td>'
        html += f'<td>{item["Price"]}</td>'
        html += f'<td>{item["Percentage Change"]}</td>'
        html += f'<td>{item["Action"]}</td>'
        html += f'<td>{item["Value"]}</td>'
        html += '</tr>'
    
    html += '</table>'
    return html

def create_html_ipo(data):
    if not data:
        html = "<p>Issue with ipo data</p>"
        return html

    html = '<table border="1" cellpadding="5" style="border-collapse: collapse; width: 100%;">'
    html += '<tr><th>Company Name</th><th>Price</th><th>GMP</th><th>Est Listing</th><th>IPO Size</th><th>Lot</th></tr>'
    
    for item in data:
        html += '<tr>'
        html += f'<td>{item["Company Name"]}</td>'
        html += f'<td>{item["Price"]}</td>'
        html += f'<td>{item["GMP"]}</td>'
        html += f'<td>{item["Est Listing"]}</td>'
        html += f'<td>{item["IPO Size"]}</td>'
        html += f'<td>{item["Lot"]}</td>'
        html += '</tr>'
    
    html += '</table>'
    return html

def send_email(recipient_name, html_table, html_table_ipo):
    sender_email = os.getenv('SENDER_EMAIL')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    password = os.getenv('MY_PASSWORD')
    email_subject = "Daily Market Update"
    if not password:
        raise ValueError("Environment variable MY_PASSWORD is not set. Please set it before running the script.")
 
    stock_data_ipo = len(fetch_data_ipo())
    stock_data = len(fetch_data())

    green= "#20B2AA"
    blue = "#0044cc"
    red = "#C21807"

    if stock_data_ipo > 3 or stock_data > 3:
        stock_data_color = green
    elif stock_data_ipo == 0 and stock_data == 0:
        stock_data_color = red
    else:
        stock_data_color = blue

    html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f9f9f9;">
            <div style="max-width: 600px; margin: 20px auto; background: white; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">

                <!-- Header Section -->
                <div style="background-color: {stock_data_color}; color: white; padding: 15px; text-align: center;">
                    <h2 style="margin: 0;">NSE Trading India</h2>
                    <p style="margin: 5px 0 0;">Your Trusted Partner in Trading</p>
                </div>

                <!-- Body Section -->
                <div style="padding: 20px;">
                    <p style="margin: 0; text-align: left;">Hi {recipient_name or 'All'},</p>
                    <p style="margin: 10px 0; text-align: left;">
                        We’re sharing the latest updates and insights in trading. Please find the details below:
                    </p>

                    <!-- First Table Section -->
                    <div id="market-updates-section" style="margin: 20px 0; overflow-x: auto; border: 1px solid #ddd; padding: 10px; border-radius: 4px;">
                        <h4 style="margin: 0 0 10px;">Market Updates</h4>
                        {html_table}
                    </div>

                    <!-- Second Table Section -->
                    <div id="ipo-updates-section" style="margin: 20px 0; overflow-x: auto; border: 1px solid {stock_data_color}; padding: 10px; border-radius: 4px; background-color: {stock_data_color};">
                        <h4 style="margin: 0 0 10px;">IPO Updates</h4>
                        {html_table_ipo}
                    </div>

                    <p style="text-align: left; margin: 20px 0;">
                        We hope you find this information useful. If you have any questions or need assistance, feel free to reach out to us.
                    </p>

                    <p style="text-align: left;">
                        Thanks and Regards,<br>
                        <strong>NSE Trading India</strong>
                    </p>
                </div>

                <!-- Footer Section -->
                <div style="background-color: #f4f4f4; color: #666; padding: 10px; text-align: center; font-size: 0.9em;">
                    <p style="margin: 0;">This is an automated email. Please do not reply to this address.</p>
                    <p style="margin: 5px 0 0;">© 2024 NSE Trading India. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>"""

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = email_subject
    message.attach(MIMEText(html_body, "html"))

    pdf_path ='pdf/company_analysis_report.pdf'
    # Attach PDF if provided
    if pdf_path:
        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_attachment = MIMEBase("application", "octet-stream")
                pdf_attachment.set_payload(pdf_file.read())
            encoders.encode_base64(pdf_attachment)
            pdf_attachment.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(pdf_path)}",
            )
            message.attach(pdf_attachment)
        except Exception as e:
            print(f"Error attaching PDF: {e}")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


if __name__ == "__main__":
    recipient_name = 'Kaushal'
    # Load environment variables from the .env file
    load_dotenv()

    # Fetch stock data
    stock_data_ipo = "None"

    # Generate the HTML table based on the data
    html_table_ipo = create_html_ipo(stock_data_ipo)

    # Fetch stock data
    stock_data = fetch_data()

    # Generate the HTML table based on the data
    html_table = create_html_table(stock_data)

    some_function()

    # Send email with the generated table
    send_email(recipient_name, html_table, html_table_ipo)
