import sys
print(sys.path)

import sys
sys.path.insert(0, r'C:\Users\shreya.kothiwal\Downloads\backend')

from controller import login_required

import controller
print(controller)

from controller.blueprint import api

from controller import api

import pdfplumber
import re
import pandas as pd
from io import BytesIO
from flask import send_file
from flask_restx import Resource, fields
from controller import login_required

pdf_path = [
    "The NIST Cybersecurity Framework (CSF) 2.0.pdf",
    "The AESCSF v2 Lite Framework.pdf",
    "SWIFT Customer Security Controls Framework.pdf",
    "PCI-DSS-v4_0.pdf",
    "NIST.SP.800-53r4.pdf",
    "NIST.SP.800-53r5.pdf",
    "ISO_IEC_27001_2022(en).pdf",
    "CIS_Microsoft_365_Foundations_Benchmark_v3.0.0.pdf"
]


def extract_text_from_pdf(pdf_path):
    """Function to extract text from a PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""  # Variable to store the extracted text
        for page in pdf.pages:  # Iterate through each page in the PDF
            text += page.extract_text()  # Extract text from the page
    return text

def extract_relevant_data(pdf_text, domains, comparison_standards, baseline_standard):
    """Function to extract relevant data from the PDF text."""
    rows = []
    
    for domain in domains:
        row = []

        # Extract control description
        control_desc = extract_control_description(pdf_text, domain, baseline_standard)
        row.append(control_desc)

        # Extract control identifier
        control_identifier = extract_control_identifier(pdf_text, domain, baseline_standard)
        row.append(control_identifier)

        # Extract control identifiers for comparison standards
        for standard in comparison_standards:
            control_identifier_comparison = extract_control_identifier_for_standard(pdf_text, domain, standard)
            row.append(control_identifier_comparison)

        # Extract implementation guidance
        implementation_guidance = extract_implementation_guidance(pdf_text, domain)
        row.append(implementation_guidance)
        
        rows.append(row)

    return rows

def extract_control_description(pdf_text, domain, baseline_standard):
    """Extract control description using regex."""
    match = re.search(rf'{domain}.*Control Description:\s*(.*)', pdf_text, re.IGNORECASE)
    return match.group(1) if match else 'N/A'

def extract_control_identifier(pdf_text, domain, baseline_standard):
    """Extract control identifier like AC-1, AC-2."""
    match = re.search(rf'{domain}.*Control Identifier:\s*(\w+-\d+)', pdf_text, re.IGNORECASE)
    return match.group(1) if match else 'N/A'

def extract_control_identifier_for_standard(pdf_text, domain, standard):
    """Extract control identifier for comparison standards."""
    match = re.search(rf'{domain}.*{standard}.*Control Identifier:\s*(\w+-\d+)', pdf_text, re.IGNORECASE)
    return match.group(1) if match else 'N/A'

def extract_implementation_guidance(pdf_text, domain):
    """Extract implementation guidance from the PDF."""
    match = re.search(rf'{domain}.*Implementation Guidance:\s*(.*)', pdf_text, re.IGNORECASE)
    return match.group(1) if match else 'N/A'

ucfModel = api.model('ucfModel', {
    'baselineStandard': fields.String(required=True),
    'comparisonStandards': fields.List(fields.String, required=True),
    'domains': fields.List(fields.String, required=True),
    'customQuery': fields.String(required=False)
})

class GenerateUCF(Resource):
    @login_required
    @api.expect(ucfModel)
    def post(self):
        data = request.get_json()
        baseline_standard = data.get('baselineStandard', '')
        comparison_standards = data.get('comparisonStandards', [])
        domains = data.get('domains', [])
        custom_query = data.get('customQuery', '')

        rows = []

        if len(domains) == 0:
            # If no domains are provided, use the baseline standard PDF to extract data
            columns = ['Control Name', 'Control Title', 'Control Description']
            columns.extend(comparison_standards)
            columns.append('Implementation Guidance')

            # Extract text from PDF based on baseline_standard
            pdf_path = f"pdfs/{baseline_standard}.pdf"  # Path to your PDF
            pdf_text = extract_text_from_pdf(pdf_path)

            # Extract relevant data
            rows = extract_relevant_data(pdf_text, comparison_standards, comparison_standards, baseline_standard)

            # Create DataFrame with the extracted data
            df = pd.DataFrame(rows, columns=columns)

            # Save DataFrame to an Excel file
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')

            output.seek(0)
            return send_file(output, download_name='controls.xlsx', as_attachment=True)
        else:
            # If domains are provided, proceed with extracting data for each domain
            columns = ['Domain', 'Control Description', baseline_standard]
            columns.extend(comparison_standards)
            columns.append('Implementation Guidance')

            for domain in domains:
                row = [domain]

                # Extract control description
                control_desc = extract_control_description(pdf_text, domain, baseline_standard)
                row.append(control_desc)

                # Extract control identifier
                base = extract_control_identifier(pdf_text, domain, baseline_standard)
                row.append(base)

                # Extract control identifiers for comparison standards
                for standard in comparison_standards:
                    standard_content = extract_control_identifier_for_standard(pdf_text, domain, standard)
                    row.append(standard_content)

                # Extract implementation guidance
                guidance = extract_implementation_guidance(pdf_text, domain)
                row.append(guidance)

                rows.append(row)

            # Create DataFrame with the extracted data
            df = pd.DataFrame(rows, columns=columns)

            # Save DataFrame to an Excel file
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')

            output.seek(0)
            return send_file(output, download_name='controls.xlsx', as_attachment=True)
