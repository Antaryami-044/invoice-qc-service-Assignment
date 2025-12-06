Invoice Quality Control Service (invoice-qc-service-[YOUR_NAME])
1. Overview

This project implements a modular Invoice Extraction and Quality Control (QC) Service).
The main goal is to process unstructured B2B invoice PDFs, extract the required financial/identity data, and validate everything using a predefined schema and business rules.

The service is accessible through:

A Command-Line Interface (CLI) using Typer

A RESTful HTTP API using FastAPI

Architecture is clean, production-ready, and fully modular.

Completed Sections (Mandatory Requirements)

Part A: Schema and Validation Rules

Part B: PDF Extraction Module

Part C: Validation Core

Part D.1: CLI Tool

Part D.2: Minimal FastAPI Server

2. Schema & Validation Design
2.1 Extracted Data Schema

Pydantic models live in:
invoice_qc/schemas.py

Field Name	Type	Category	Description
invoice_id	str	Identifier	Unique ID for the input file
invoice_number	str	Identifier	Official invoice number
invoice_date	date	Date/Time	Invoice issue date
due_date	date	Date/Time	Final payment date
seller_name	str	Parties	Seller company name
seller_tax_id	str	Parties	Seller VAT/Tax ID
buyer_name	str	Parties	Buyer company name
buyer_tax_id	str	Parties	Buyer VAT/Tax ID
currency	str	Money	ISO currency code
net_total	float	Money	Subtotal before tax
tax_amount	float	Money	Total tax
gross_total	float	Money	Net + Tax
line_items	List[LineItem]	Details	List of items (description, qty, price, total)
2.2 Validation Rules

Validation logic lives in:
invoice_qc/validator.py

Category	Rule ID	Rule Description	Rationale
Completeness/Format	RUL_001_CRITICAL_FIELDS	invoice_number, invoice_date, seller_name, gross_total must exist	Essential for accounting
Completeness/Format	RUL_002_KNOWN_CURRENCY	currency ∈ {EUR, USD, INR, GBP}	Standard financial currencies
Completeness/Format	RUL_003_NON_NEGATIVE_TOTALS	net_total, tax_amount, gross_total ≥ 0	Prevent bad extractions
Business Rules	RUL_101_TOTALS_MATCH	ABS(gross_total − (net_total + tax_amount)) < 0.01	Core accounting identity
Business Rules	RUL_102_DUE_DATE_LOGIC	due_date ≥ invoice_date	Payment timeline accuracy
Anomaly Detection	RUL_201_LINE_TOTAL_SUM	ABS(net_total − sum(line_totals)) < 0.01	Line-item consistency
3. Architecture

The system uses a layered, modular architecture:

invoice-qc-service-[YOUR_NAME]/
├── invoice_qc/
│   ├── __init__.py
│   ├── cli.py
│   ├── api.py
│   ├── schemas.py
│   ├── extractor.py
│   └── validator.py
├── pdfs/
├── requirements.txt
└── README.md

System Flow
[Invoice PDFs]
       |
       | 1. Extraction (extractor.py)
       v
Structured JSON
       |
       | 2. Validation (validator.py)
       v
QC Report


Interfaces:

CLI → Read PDFs → Extract → Validate → Save Reports

API → Validate structured JSON via /validate-json

4. Setup & Installation
Prerequisites

Python 3.9+

Sample invoice PDFs placed inside /pdfs/

Steps
git clone https://github.com/[YOUR_GITHUB_USER]/invoice-qc-service-[YOUR_NAME].git
cd invoice-qc-service-[YOUR_NAME]


Create virtual env:

python -m venv venv


Activate:

Windows

.\venv\Scripts\activate


Linux/macOS

source venv/bin/activate


Install dependencies:

pip install -r requirements.txt

5. Usage
5.1 CLI Commands

Run from project root.

Full Run (Extract + Validate)
python -m invoice_qc.cli full-run --pdf-dir pdfs --report report.json

Extract Only
python -m invoice_qc.cli extract --pdf-dir pdfs --output data.json

Validate Only
python -m invoice_qc.cli validate --input data.json --report report_only.json

5.2 HTTP API (FastAPI)

Run server:

uvicorn invoice_qc.api:app --reload


Docs:
http://127.0.0.1:8000/docs

Health Check
curl -X GET "http://127.0.0.1:8000/health"


Expected response:

{"status": "ok", "message": "Invoice QC Service is running."}

Validate JSON
curl -X POST "http://127.0.0.1:8000/validate-json" \
     -H "Content-Type: application/json" \
     -d @extracted_invoices.json

6. Video Explanation

Provide your video link here:

[YOUR_VIDEO_LINK]

7. AI Usage Notes

Tools used:

Gemini (LLM)

GitHub Copilot

Roles:

Architectural validation

Boilerplate generation (CLI & API)

Regex + parsing optimization

Avoiding blocking I/O in FastAPI

Example correction:

AI initially proposed synchronous file upload handling.
Updated to async (await file.read()) for scalability.

8. Assumptions & Limitations

Extraction relies heavily on regex tuned for your sample PDFs

Table parsing may fail on complex/multiline layouts

No database / no historical QC

Line-item extraction optimized for simple columns