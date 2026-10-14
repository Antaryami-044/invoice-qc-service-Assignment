# 🧾 Invoice Quality Control Service (`invoice-qc-service-Antaryami-Sahu`)

A modular, production-ready Invoice Extraction and Quality Control (QC) service. This project processes unstructured B2B invoice PDFs, extracts identity and financial data, and runs validation checks against a strict Pydantic schema and core accounting business rules.

---

## 1. Overview

The service extracts structured data from PDF invoices and performs automated compliance checks through two primary interfaces:
* **Command-Line Interface (CLI):** Powered by `Typer` for batch processing and local pipelines.
* **RESTful HTTP API:** Powered by `FastAPI` for service integration and real-time validation.

---

## 2. Completed Sections

- [x] **Part A: Schema and Validation Rules** (Structured models and accounting checks)
- [x] **Part B: PDF Extraction Module** (`invoice_qc/extractor.py`)
- [x] **Part C: Validation Core** (`invoice_qc/validator.py`)
- [x] **Part D.1: CLI Tool** (`invoice_qc/cli.py`)
- [x] **Part D.2: Minimal FastAPI Server** (`invoice_qc/api.py`)

---

## 3. Schema & Validation Design

### 3.1 Extracted Data Schema
Models are implemented using Pydantic in `invoice_qc/schemas.py`:

| Field Name | Type | Category | Description |
| :--- | :--- | :--- | :--- |
| `invoice_id` | `str` | Identifier | Unique ID for the input file |
| `invoice_number` | `str` | Identifier | Official invoice number |
| `invoice_date` | `date` | Date/Time | Invoice issuance date |
| `due_date` | `date` | Date/Time | Payment due date |
| `seller_name` | `str` | Parties | Seller legal entity name |
| `seller_tax_id` | `str` | Parties | Seller VAT/Tax identification number |
| `buyer_name` | `str` | Parties | Buyer legal entity name |
| `buyer_tax_id` | `str` | Parties | Buyer VAT/Tax identification number |
| `currency` | `str` | Money | ISO 4217 currency code |
| `net_total` | `float` | Money | Subtotal before taxes |
| `tax_amount` | `float` | Money | Total tax charge |
| `gross_total` | `float` | Money | Total payable amount (`net_total + tax_amount`) |
| `line_items` | `List[LineItem]` | Details | Itemized records (description, qty, price, total) |

---

### 3.2 Validation Rules
Business logic is implemented in `invoice_qc/validator.py`:

| Category | Rule ID | Rule Description | Rationale |
| :--- | :--- | :--- | :--- |
| **Completeness/Format** | `RUL_001_CRITICAL_FIELDS` | `invoice_number`, `invoice_date`, `seller_name`, `gross_total` must exist | Essential fields required for valid accounting |
| **Completeness/Format** | `RUL_002_KNOWN_CURRENCY` | `currency` $\in$ {EUR, USD, INR, GBP} | Enforce accepted international currency codes |
| **Completeness/Format** | `RUL_003_NON_NEGATIVE_TOTALS` | `net_total`, `tax_amount`, `gross_total` $\ge$ 0 | Prevent invalid or negative monetary values |
| **Business Rules** | `RUL_101_TOTALS_MATCH` | $ABS(\text{gross\_total} - (\text{net\_total} + \text{tax\_amount})) < 0.01$ | Core accounting identity validation |
| **Business Rules** | `RUL_102_DUE_DATE_LOGIC` | `due_date` $\ge$ `invoice_date` | Ensure logical payment terms and timelines |
| **Anomaly Detection** | `RUL_201_LINE_TOTAL_SUM` | $ABS(\text{net\_total} - \sum(\text{line\_totals})) < 0.01$ | Check line-item aggregation against stated subtotal |

---

## 4. Architecture and Flow

```plaintext
invoice-qc-service-Antaryami-Sahu/
├── invoice_qc/
│   ├── __init__.py
│   ├── cli.py         # CLI interface (Typer)
│   ├── api.py         # RESTful API interface (FastAPI)
│   ├── schemas.py     # Pydantic models for data definitions
│   ├── extractor.py   # PDF text parsing & regex extraction logic
│   └── validator.py   # Accounting and business rule validation
├── pdfs/              # Sample input invoices
├── requirements.txt   # Project dependencies
└── README.md
```

---

## 5. Setup & Installation

### Prerequisites
- Python 3.9+
- Sample PDF invoices placed in the `./pdfs/` directory

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Antaryami-044/invoice-qc-service-Assignment.git
   cd invoice-qc-service-Assignment
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows (Command Prompt)
   python -m venv venv
   .\venv\Scripts\activate

   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 6. Usage

### 6.1 CLI Interface (Typer)

Execute commands directly from the project root directory:

| Command | Description | Example |
| :--- | :--- | :--- |
| **Full Run** | Extracts PDF data and runs validation in one pass | `python -m invoice_qc.cli full-run --pdf-dir pdfs --report report.json` |
| **Extract Only** | Parses PDFs into structured JSON | `python -m invoice_qc.cli extract --pdf-dir pdfs --output data.json` |
| **Validate Only** | Validates an existing JSON dataset against rules | `python -m invoice_qc.cli validate --input data.json --report report_only.json` |

---

### 6.2 HTTP API (FastAPI)

1. **Start the local server:**
   ```bash
   uvicorn invoice_qc.api:app --reload
   ```

2. **Health Check (`GET /health`):**
   ```bash
   curl -X GET "[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)"
   ```
   *Expected Response:*
   ```json
   {
     "status": "ok",
     "message": "Invoice QC Service is running."
   }
   ```

3. **Validate Extracted JSON (`POST /validate-json`):**
   ```bash
   curl -X POST "[http://127.0.0.1:8000/validate-json](http://127.0.0.1:8000/validate-json)" \
        -H "Content-Type: application/json" \
        -d @extracted_invoices.json
   ```

---

## 7. AI Usage & Engineering Refinements

Large Language Models (LLMs) were integrated into the development workflow for rapid scaffolding and technical review:

| Tool Used | Primary Roles | Key Correction / Refinement |
| :--- | :--- | :--- |
| **Gemini (LLM)** | Architecture planning, regex extraction tuning | Resolved blocking synchronous file reads in FastAPI by shifting to non-blocking async execution patterns. |
| **GitHub Copilot** | CLI argument templates, API schema boilerplate | Fixed initial auto-generated synchronous route handlers into full `async def` implementations with `await file.read()`. |

---

## 8. Assumptions & Limitations

- **Template-Dependent Regex:** Extraction patterns are tuned to standard layout formats matching the target PDF dataset.
- **Complex Tables:** Highly variable table designs, split columns, or multiline row items across page breaks may require fine-tuning.
- **Stateless Operation:** The system processes data in-memory without persistent database storage or historical run metrics.
- **Standard Line Layouts:** Line-item extraction assumes structured column alignment (Quantity, Description, Unit Price, Total).

---

## 9. Walkthrough Video

- **Loom :** [Watch the Video Walkthrough](https://www.loom.com/share/097595daa98f4a9ab85a0d3a90e3f2fe)
