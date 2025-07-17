# tools.py
from crewai.tools import BaseTool
from user_functions_2 import analyze_legal_clauses, analyze_financial_clauses
from clause_tools import load_clause_templates, generate_clause
from utils import extract_text_from_pdf
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfMerger
from reportlab.pdfgen import canvas
import os
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PyPDF2 import PdfReader, PdfWriter


class DummyLegalClauseChecker(BaseTool):
    name: str = "legal_clause_checker"
    description: str = "Identifies missing legal clauses from a document."

    def _run(self, file_name: str):

        legal_mandatory, legal_optional, _, _, _ = load_clause_templates()
        legal_clauses_all = legal_mandatory + legal_optional
        document_text = ""

        file_path = f"./uploaded/{file_name}"
        try:
            with open(file_path, "rb") as f:
                    document_text = extract_text_from_pdf(f)
        except Exception as e:
            return f"Error reading file: {str(e)}"

        print(f"document extracted: {document_text}")
        legal_result = eval(analyze_legal_clauses(document_text, legal_clauses_all))

        present_mandatory = [c for c in legal_result["present"] if c in legal_mandatory]
        present_optional = [c for c in legal_result["present"] if c in legal_optional]
        missing_mandatory = [c for c in legal_result["missing"] if c in legal_mandatory]
        missing_optional = [c for c in legal_result["missing"] if c in legal_optional]

        def render_table():
                max_rows = max(len(present_mandatory), len(present_optional), len(missing_mandatory) + len(missing_optional))
                def format_cell(val, highlight=False):
                    if not val: return ""
                    if highlight:
                        return f"<span style='color:red;font-weight:bold'>⚠️ {val}</span>"
                    return val
                rows = []
                for i in range(max_rows):
                    row = {
                        "primary": present_mandatory[i] if i < len(present_mandatory) else "",
                        "optional": present_optional[i] if i < len(present_optional) else "",
                        "missing": ""
                    }
                    if i < len(missing_mandatory):
                        row["missing"] = format_cell(missing_mandatory[i], highlight=True)
                    elif i - len(missing_mandatory) < len(missing_optional):
                        idx = i - len(missing_mandatory)
                        row["missing"] = format_cell(missing_optional[idx])
                    rows.append(row)

                html = """
                <style>
                    table { border-collapse: collapse; width: 100%; margin-top: 1rem; font-family: sans-serif; }
                    th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
                    th { background-color: #f0f0f0; }
                </style>
                <table>
                    <thead><tr>
                        <th>✅ Primary Clauses</th>
                        <th>📘 Optional Clauses</th>
                        <th>❌ Missing Clauses</th>
                    </tr></thead><tbody>
                """
                for row in rows:
                    html += f"<tr><td>{row['primary']}</td><td>{row['optional']}</td><td>{row['missing']}</td></tr>"
                html += "</tbody></table>"
                return html


        response = render_table()
        return response

class DummyFinanceClauseChecker(BaseTool):
    name: str = "finance_clause_checker"
    description: str = "Identifies missing financial clauses from a document."

    def _run(self, file_name: str):
        _, _, financial_mandatory, financial_optional, _ = load_clause_templates()
        financial_clauses_all = financial_mandatory + financial_optional
        document_text = ""

        file_path = f"./uploaded/{file_name}"
        try:
            with open(file_path, "rb") as f:
                    document_text = extract_text_from_pdf(f)
        except Exception as e:
            return f"Error reading file: {str(e)}"

        print(f"document extracted: {document_text}")


        financial_result = eval(analyze_financial_clauses(document_text, financial_clauses_all))

        present_mandatory = [c for c in financial_result["present"] if c in financial_mandatory]
        present_optional = [c for c in financial_result["present"] if c in financial_optional]
        missing_mandatory = [c for c in financial_result["missing"] if c in financial_mandatory]
        missing_optional = [c for c in financial_result["missing"] if c in financial_optional]

        def render_table():
                max_rows = max(len(present_mandatory), len(present_optional), len(missing_mandatory) + len(missing_optional))
                def format_cell(val, highlight=False):
                    if not val: return ""
                    if highlight:
                        return f"<span style='color:red;font-weight:bold'>⚠️ {val}</span>"
                    return val
                rows = []
                for i in range(max_rows):
                    row = {
                        "primary": present_mandatory[i] if i < len(present_mandatory) else "",
                        "optional": present_optional[i] if i < len(present_optional) else "",
                        "missing": ""
                    }
                    if i < len(missing_mandatory):
                        row["missing"] = format_cell(missing_mandatory[i], highlight=True)
                    elif i - len(missing_mandatory) < len(missing_optional):
                        idx = i - len(missing_mandatory)
                        row["missing"] = format_cell(missing_optional[idx])
                    rows.append(row)

                html = """
                <style>
                    table { border-collapse: collapse; width: 100%; margin-top: 1rem; font-family: sans-serif; }
                    th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
                    th { background-color: #f0f0f0; }
                </style>
                <table>
                    <thead><tr>
                        <th>✅ Primary Clauses</th>
                        <th>📘 Optional Clauses</th>
                        <th>❌ Missing Clauses</th>
                    </tr></thead><tbody>
                """
                for row in rows:
                    html += f"<tr><td>{row['primary']}</td><td>{row['optional']}</td><td>{row['missing']}</td></tr>"
                html += "</tbody></table>"
                return html


        response = render_table()
        return response


# class ChatAnswerer(BaseTool):
#     name: str = "chat_answerer"
#     description: str = "Answers questions based on the content of a contract document."
#     def _run(self,file_name:str):
#         return(
#             "Hi this is chat agent how can i help you"
#         )


class EmailSender(BaseTool):
     name: str = "email_sender"
     description: str = 'Sends email'

     def _run(self,file_name: str):
        sender_email = "vigneshkumarsof94@gmail.com"
        receiver_email = "vedhanarayanan2002@gmail.com"
        app_password = "xtrelokjjamdsvbg"
        # app_password = ""
        subject = "Test Email from Python"
        body = "Hi there, Please find the attached document for review."

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject


        message.attach(MIMEText(body, "plain"))

        # File to attach
        file_path = f"./generated_doc/{file_name}"  # Replace with your file path

        # Add the file as an attachment
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode the file in base64
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(file_path)}"
            )
            message.attach(part)
        except FileNotFoundError:
            print("❌ File not found:", file_path)
            exit()

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()  
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()
            print("✅ Email sent successfully.")
        except Exception as e:
            print("❌ Failed to send email:", e) 
        return ("Email sent successfully")
     
# class AddClause(BaseTool):
#     name: str = "Add_clause"
#     description: str = 'Adds the generated clause to the file' 
#     def _run(self,content:str,file_name: str):
#         file_path  = f"./uploaded/{file_name}"
        
#         def create_append_page(text, output_path="./generated_doc/append_page.pdf"):
#             c = canvas.Canvas(output_path, pagesize=A4)
#             width, height = A4
#             c.drawString(72, height - 100, text)
#             c.save()

#         def append_text_to_pdf(original_pdf_path, new_text, output_pdf_path):
#             # Step 1: Create a new PDF page with the text
#             append_pdf_path = "./generated_doc/append_page.pdf"
#             create_append_page(new_text, append_pdf_path)

#             # Step 2: Merge original + new page
#             merger = PdfMerger()
#             merger.append(original_pdf_path)
#             merger.append(append_pdf_path)
#             merger.write(output_pdf_path)
#             merger.close()

#             # Clean up the temporary page
#             os.remove(append_pdf_path)

#         append_text_to_pdf(file_path, content, f"./generated_doc/{file_name}")
        
#         return(f"Clause added successfully for the file {file_name}")

import io
import os
from typing import List
from PyPDF2 import PdfReader, PdfWriter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from crewai.tools import BaseTool

class AddClause(BaseTool):
    name: str = "Add_clause"
    description: str = "Generates a contract clause and returns it to be stored or appended."

    def _run(self, content: str, file_name: str) -> str:
        return content.strip()  # The actual storing is done in app.py
        

class DownloadClauseTool(BaseTool):
    name: str = "Download_clause_file"
    description: str = "Generates the updated contract PDF with appended clauses."

    def _run(self, file_name: str, new_clauses: List[dict]) -> bytes:
        upload_path = f"./uploaded/{file_name}"
        output_path = f"./generated_doc/{file_name}" 

        def create_clause_appendix_pdf(clauses):
            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=A4)
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name="ClauseTitle", fontSize=12, leading=14, textColor=colors.black))
            styles.add(ParagraphStyle(name="ClauseBody", fontSize=11, leading=14, spaceAfter=8))  # renamed here

            flow = [Paragraph(" Terms and Conditions", styles["Heading2"]), Spacer(1, 12)]
            for clause in clauses:
                flow.append(Paragraph(f"<b>{clause['name']}</b>", styles["ClauseTitle"]))
                flow.append(Paragraph(clause['text'].replace("\n", "<br/>"), styles["ClauseBody"]))  # use renamed style
                flow.append(Spacer(1, 10))

            doc.build(flow)
            buf.seek(0)
            return buf


        writer = PdfWriter()
        reader = PdfReader(upload_path)
        for page in reader.pages:
            writer.add_page(page)

        appendix_pdf = create_clause_appendix_pdf(new_clauses)
        appendix_reader = PdfReader(appendix_pdf)
        for page in appendix_reader.pages:
            writer.add_page(page)

        final_buf = io.BytesIO()
        writer.write(final_buf)
        final_buf.seek(0)
        with open(output_path, "wb") as f:
            f.write(final_buf.getbuffer())
        return final_buf.read()
