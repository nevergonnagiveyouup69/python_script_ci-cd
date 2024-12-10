from datetime import datetime
from script import fetch_data
from alpha import get_company_url
import time
from fpdf import FPDF # type: ignore
import google.generativeai as genai # type: ignore
import os
import datetime

def make_pdf():
    # Define conditions for each field
    def get_text_color(key, value):
        try:
            # Remove symbols and convert to float for numeric comparison
            clean_value = float(value)
        except (ValueError, TypeError):
            # Return black for non-numeric or invalid data
            return (0, 0, 0)
        
        # Conditional logic for specific fields
        if key == "Debt":
            return (255, 0, 0) if clean_value >= 0 else (0, 255, 0)
        elif key == "P/E":
            return (255, 0, 0) if 15 > clean_value > 25 else (0, 255, 0)
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
            # Default black for other fields
            return (0, 0, 0)
            
    # Subclass FPDF for footer implementation
    class PDFWithFooter(FPDF):
        def footer(self):
            # Skip numbering the title page (first page)
            if self.page_no() > 1:
                self.set_y(-15)  # Position footer at 15mm from the bottom
                self.set_font('DejaVu', size=8)
                self.cell(0, 10, f"Page {self.page_no() - 1}", align='C')  # Adjust page number


    # Start the timer
    start_time = time.time()

    # Initialize the PDF
    pdf = PDFWithFooter()
    pdf.set_auto_page_break(auto=True, margin=15)
    # Add a title page
    pdf.add_page()
    # Get page dimensions
    page_width = pdf.w
    page_height = pdf.h

    # Place the image as full-page background
    pdf.image("screenshots/without_bg.jpg", x=0, y=0, w=page_width, h=page_height)

    # Add custom fonts
    pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
    pdf.add_font('DancingScript', '', 'fonts/DancingScript-VariableFont_wght.ttf', uni=True)
    pdf.add_font('Secular', '', 'fonts/SecularOne-Regular.ttf', uni=True)
    pdf.add_font('pirataone', '', 'fonts/PirataOne-Regular.ttf', uni=True)

    # Title Section
    pdf.set_font('pirataone', size=65)  # Reduced font size
    pdf.set_text_color(0, 0, 0)  # Set black color for the title

    # Add spacing and properly center the title
    pdf.cell(0, 40, "", ln=True)  # Add vertical space
    pdf.multi_cell(0, 20, "Company", align='C')  # Multi-line title to ensure wrapping

    pdf.set_font('pirataone', size=85)  # Reduced font size
    pdf.set_text_color(0, 0, 0)  # Set black color for the title
    pdf.cell(0, 5, "", ln=True)  # Add vertical space
    pdf.multi_cell(0, 20, "Analysis Report", align='C')  # Multi-line title to ensure wrapping

    # Subtitle Section
    pdf.ln(10)  # Add spacing between title and subtitle
    pdf.set_font('Secular', size=25)  # Helvetica is a core font similar to Arial
    pdf.set_text_color(0, 0, 0)  # Black color for the rest of the text
    pdf.cell(0, 10, f"{datetime.datetime.now().strftime('%B %d, %Y')}", ln=True, align='C')  # Centered date
    pdf.ln(10)

    # Fetch data
    data = fetch_data()
    grouped_data = {}

    # Group data by Company Name
    for record in data:
        company_name = record['Company Name']
        grouped_data.setdefault(company_name, []).append(record)

    # Generate analysis for each company
    for company, acquisitions in grouped_data.items():
        analysis_value = get_company_url(company)

        # Configure GenAI
        
        if analysis_value and len(analysis_value) > 1:
            genai.configure(api_key=os.getenv('API_KEY_GEN'))
            model = genai.GenerativeModel("gemini-1.5-flash")
            try:
                response = model.generate_content(
                    f"Pretend you are professional analyst. I want you to analyze the insider data of this stock and give a one-paragraph explanation if it is worth investing today: {acquisitions}\nFundamental: {analysis_value[1]}"
                )
                total_analysis = response.text
            except Exception as e:
                print(f"Error generating analysis for {company}: {e}")
                total_analysis = "Analysis could not be generated."
        else:
            print(f"Invalid or incomplete data for company {company}: {analysis_value}")
            total_analysis = "No valid data available for analysis."

        # Add a new page for each company
        pdf.add_page()
        pdf.set_draw_color(200, 200, 200)  # Light gray
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())

        # Add company name as a header
        pdf.set_font('Secular', size=14) 
        pdf.cell(0, 10, f"Company: {company}", ln=True, align='L')
        pdf.ln(5)

        pdf.set_font('Secular', size=14)
        pdf.cell(0, 10, "Profitability:", ln=True, align='L')

        pdf.set_font('DancingScript', size=14)
        if analysis_value and isinstance(analysis_value[0], str):
            if analysis_value[0] in ['Low', 'None']:
                pdf.set_text_color(197, 24, 7)  # Red
            elif analysis_value[0] == 'High':
                pdf.set_text_color(144, 238, 144)  # Light Green
            elif analysis_value[0] == 'Very High':
                pdf.set_text_color(32, 178, 170)  # Light Sea Green
            else:
                pdf.set_text_color(252, 238, 167)  # Light Yellow

            pdf.cell(f"{analysis_value[0]}")
            print(f"this shit:  {analysis_value[0]}")
        else:
            pdf.cell(0, 10, "N/A", ln=True, align='R')  # Fallback if invalid
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)

        
        # Add a separator for visual clarity
        pdf.set_draw_color(200, 200, 200)  # Light gray
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())

        for key, value in data[2].items():
            pdf.cell(50, 10, key, border=0)
            pdf.cell(100, 10, str(value), border=0)
            pdf.ln(10)  # Move to the next row
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())  # Add a horizontal line for each row

        # Add Fundamental Analysis
        pdf.set_font('Secular', size=14)
        pdf.cell(0, 10, "Fundamental Analysis:", ln=True)
        pdf.set_font('DejaVu', size=10)
        pdf.multi_cell(0, 10, str(analysis_value[1]))
        pdf.ln(5)

        # Add table header
        pdf.set_font('DejaVu', size=10)
        pdf.set_fill_color(200, 220, 255)  # Light blue background for headers
        pdf.cell(95, 10, "Metric", border=1, align='C', fill=True)
        pdf.cell(95, 10, "Value", border=1, align='C', fill=True)
        pdf.ln()

        if analysis_value and len(analysis_value) > 2 and analysis_value[2]:
            for key, value in analysis_value[2].items():
                 # Get text color based on conditions
                # Add key and value cells
                pdf.set_text_color(0, 0, 0) 
                pdf.cell(95, 10, key, border=1, align='L')
                color = get_text_color(key, value)
                pdf.set_text_color(*color)
                pdf.cell(95, 10, str(value), border=1, align='L')
                pdf.set_text_color(0, 0, 0) 
                pdf.ln()
                # Add additional spacing
        else:
            print("analysis_value[2] is not available.")
           

        pdf.ln(5)

        # Add Insider Data Analysis
        pdf.set_font('Secular', size=14)
        pdf.cell(0, 10, "Insider Data Analysis:", ln=True)
        pdf.set_font('DejaVu', size=10)
        pdf.multi_cell(0, 10, total_analysis)
        pdf.ln(5)


        # Add table header
        pdf.set_fill_color(200, 200, 200)  # Gray background for header
        pdf.set_text_color(0, 0, 0)        # Black text

    # Save the PDF
    output_path = "pdf/company_analysis_report.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    print(f"PDF created successfully: {output_path}")

    # End the timer
    end_time = time.time()

    # Calculate the duration
    duration = end_time - start_time
    print(f"The command took {duration:.6f} seconds to run.")
