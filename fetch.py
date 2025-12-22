from datetime import datetime
from script import fetch_data
from alpha import get_company_url
import time
from fpdf import FPDF  # type: ignore
import random
import os

# Import the correct SDK
from google import genai  # type: ignore

def make_pdf():
    def get_text_color(key, value):
        try:
            clean_value = float(value)
        except (ValueError, TypeError):
            return (0, 0, 0)
        if key == "Debt":
            return (255, 0, 0) if clean_value >= 0 else (0, 255, 0)
        elif key == "P/E":
            return (255, 0, 0) if clean_value < 15 or clean_value > 25 else (0, 255, 0)
        elif key == "P/B":
            return (255, 0, 0) if clean_value > 3 else (0, 255, 0)
        elif key == "Dividend Yield":
            return (0, 255, 0) if 2 <= clean_value <= 5 else (255, 0, 0)
        elif key == "Cash":
            return (0, 255, 0) if clean_value > 0 else (255, 0, 0)
        elif key == "Promoter Holding":
            return (0, 255, 0) if clean_value > 30 else (255, 0, 0)
        elif key == "Sales":
            return (0, 255, 0) if clean_value > 10 else (255, 0, 0)
        elif key == "ROE":
            return (0, 255, 0) if clean_value > 15 else (255, 0, 0)
        elif key == "ROCE":
            return (0, 255, 0) if clean_value > 15 else (255, 0, 0)
        else:
            return (0, 0, 0)

    class PDFWithFooter(FPDF):
        def footer(self):
            if self.page_no() > 1:
                self.set_y(-15)
                self.set_font('DejaVu', size=8)
                self.cell(0, 10, f"Page {self.page_no() - 1}", align='C')

    start_time = time.time()
    pdf = PDFWithFooter()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    pdf.image("screenshots/without_bg.jpg", x=0, y=0, w=pdf.w, h=pdf.h)

    pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
    pdf.add_font('DancingScript', '', 'fonts/DancingScript-VariableFont_wght.ttf', uni=True)
    pdf.add_font('Secular', '', 'fonts/SecularOne-Regular.ttf', uni=True)
    pdf.add_font('pirataone', '', 'fonts/PirataOne-Regular.ttf', uni=True)

    pdf.set_font('pirataone', size=65)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 40, "", ln=True)
    pdf.multi_cell(0, 20, "Company", align='C')
    pdf.set_font('pirataone', size=85)
    pdf.cell(0, 5, "", ln=True)
    pdf.multi_cell(0, 20, "Analysis Report", align='C')
    pdf.ln(10)

    pdf.set_font('Secular', size=25)
    pdf.cell(0, 10, f"{datetime.now().strftime('%B %d, %Y')}", ln=True, align='C')
    pdf.ln(10)

    data = fetch_data()
    grouped_data = {}
    for record in data:
        company_name = record['Company Name']
        grouped_data.setdefault(company_name, []).append(record)

    # Init GenAI client
    client = genai.Client(api_key=os.getenv("API_KEY_GEN"))

    for company, acquisitions in grouped_data.items():
        analysis_value = get_company_url(company)

        # Generate insider data analysis text
        total_analysis = "No analysis available."
        if acquisitions and analysis_value and len(analysis_value) > 1:
            prompt_text = (
                "Pretend you are a professional analyst. "
                "Provide a concise one-paragraph explanation "
                "if this company is worth investing in today based on insider acquisition data: "
                f"{acquisitions}\nFundamental: {analysis_value[1]}"
            )

            max_retries = 5
            retry_count = 0
            while retry_count < max_retries:
                try:
                    resp = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt_text
                    )
                    total_analysis = resp.text.strip()
                    break
                except Exception as e:
                    if "429" in str(e):
                        retry_count += 1
                        wait_time = 2 ** retry_count
                        print(f"Rate limit for {company}, waiting {wait_time}s ({retry_count}/{max_retries})")
                        time.sleep(wait_time + random.uniform(0, 1))
                    else:
                        print(f"Error generating analysis for {company}: {e}")
                        total_analysis = "Analysis error: " + str(e)
                        break

        # Add new PDF page and content
        pdf.add_page()
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())

        pdf.set_font('Secular', size=14)
        pdf.cell(0, 10, f"Company: {company}", ln=True)
        pdf.ln(5)
        pdf.cell(40, 10, "Profitability: ", ln=0)

        if analysis_value and isinstance(analysis_value[0], str):
            val = analysis_value[0].strip()
            color = (0, 0, 0)
            if val in ["Low", "None"]:
                color = (197, 24, 7)
            elif val == "High":
                color = (144, 238, 144)
            elif val == "Very High":
                color = (32, 178, 170)
            pdf.set_text_color(*color)
            pdf.cell(10, 10, val)
        else:
            pdf.cell(0, 10, "N/A", ln=True)

        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

        pdf.set_font('Secular', size=14)
        pdf.cell(0, 10, "Fundamental Analysis:", ln=True)
        pdf.set_font('DejaVu', size=10)
        pdf.multi_cell(0, 10, str(analysis_value[1]))
        pdf.ln(5)

        pdf.set_font('DejaVu', size=10)
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(95, 10, "Metric", 1, align='C', fill=True)
        pdf.cell(95, 10, "Value", 1, align='C', fill=True)
        pdf.ln()

        if analysis_value and len(analysis_value) > 2 and analysis_value[2]:
            for key, value in analysis_value[2].items():
                pdf.set_text_color(0, 0, 0)
                pdf.cell(95, 10, key, border=1)
                color = get_text_color(key, value)
                pdf.set_text_color(*color)
                pdf.cell(95, 10, str(value), border=1)
                pdf.set_text_color(0, 0, 0)
                pdf.ln()

        pdf.ln(5)
        pdf.set_font('Secular', size=14)
        pdf.cell(0, 10, "Insider Data Analysis:", ln=True)
        pdf.set_font('DejaVu', size=10)
        pdf.multi_cell(0, 10, total_analysis)
        pdf.ln(5)

    output_path = "pdf/company_analysis_report.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    print(f"PDF created successfully: {output_path}")

    print(f"Took {time.time() - start_time:.2f} seconds")
