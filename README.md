# 🧾 Invoice Quality Control Service (invoice-qc-service-Antaryami-Sahu)

## 1. Overview

This project implements a modular **Invoice Extraction and Quality Control (QC) Service**. [cite_start]The main goal is to process unstructured B2B invoice PDFs, extract the required financial/identity data, and validate everything using a predefined schema and business rules[cite: 1].

The service is designed to be production-ready and accessible through two primary interfaces:
* [cite_start]A **Command-Line Interface (CLI)** using **Typer**[cite: 1].
* [cite_start]A **RESTful HTTP API** using **FastAPI**[cite: 1].

[cite_start]The architecture is clean, production-ready, and fully modular[cite: 1].

---

## 2. Completed Sections (Mandatory Requirements)

The following components and requirements have been fully implemented:

* [cite_start]**Part A:** Schema and Validation Rules[cite: 1].
* [cite_start]**Part B:** PDF Extraction Module (`extractor.py`)[cite: 1].
* [cite_start]**Part C:** Validation Core (`validator.py`)[cite: 1].
* [cite_start]**Part D.1:** CLI Tool (`cli.py`)[cite: 1].
* [cite_start]**Part D.2:** Minimal FastAPI Server (`api.py`)[cite: 1].

---

## 3. Schema & Validation Design

### 3.1 Extracted Data Schema

[cite_start]Pydantic models live in `invoice_qc/schemas.py`[cite: 1].

| Field Name | Type | Category | Description |
| :--- | :--- | :--- | :--- |
| `invoice_id` | `str` | Identifier | [cite_start]Unique ID for the input file [cite: 1] |
| `invoice_number` | `str` | Identifier | [cite_start]Official invoice number [cite: 1] |
| `invoice_date` | `date` | Date/Time | [cite_start]Invoice issue date [cite: 1] |
| `due_date` | `date` | Date/Time | [cite_start]Final payment date [cite: 1] |
| `seller_name` | `str` | Parties | [cite_start]Seller company name [cite: 1] |
| `seller_tax_id` | `str` | Parties | [cite_start]Seller VAT/Tax ID [cite: 1] |
| `buyer_name` | `str` | Parties | [cite_start]Buyer company name [cite: 1] |
| `buyer_tax_id` | `str` | Parties | [cite_start]Buyer VAT/Tax ID [cite: 1] |
| `currency` | `str` | Money | [cite_start]ISO currency code [cite: 1] |
| `net_total` | `float` | Money | [cite_start]Subtotal before tax [cite: 1] |
| `tax_amount` | `float` | Money | [cite_start]Total tax [cite: 1] |
| `gross_total` | `float` | Money | [cite_start]Net + Tax [cite: 1] |
| `line_items` | `List[LineItem]` | Details | [cite_start]List of items (description, qty, price, total) [cite: 1] |

### 3.2 Validation Rules

[cite_start]Validation logic lives in `invoice_qc/validator.py`[cite: 1].

| Category | Rule ID | Rule Description | Rationale |
| :--- | :--- | :--- | :--- |
| Completeness/Format | `RUL_001_CRITICAL_FIELDS` | [cite_start]`invoice_number`, `invoice_date`, `seller_name`, `gross_total` must exist [cite: 1] | [cite_start]Essential for accounting [cite: 1] |
| Completeness/Format | `RUL_002_KNOWN_CURRENCY` | [cite_start]`currency` $\in$ {EUR, USD, INR, GBP} [cite: 1] | [cite_start]Standard financial currencies [cite: 1] |
| Completeness/Format | `RUL_003_NON_NEGATIVE_TOTALS` | [cite_start]`net_total`, `tax_amount`, `gross_total` $\geq$ 0 [cite: 1] | [cite_start]Prevent bad extractions [cite: 1] |
| Business Rules | `RUL_101_TOTALS_MATCH` | [cite_start]$ABS(\text{gross\_total} - (\text{net\_total} + \text{tax\_amount})) < 0.01$ [cite: 1] | [cite_start]Core accounting identity [cite: 1] |
| Business Rules | `RUL_102_DUE_DATE_LOGIC` | [cite_start]`due_date` $\geq$ `invoice_date` [cite: 1] | [cite_start]Payment timeline accuracy [cite: 1] |
| Anomaly Detection | `RUL_201_LINE_TOTAL_SUM` | [cite_start]$ABS(\text{net\_total} - \sum(\text{line\_totals})) < 0.01$ [cite: 1] | [cite_start]Line-item consistency [cite: 1] |

---

## 4. Architecture and Flow

The system uses a layered, modular architecture:

invoice-qc-service-Antaryami-Sahu/ ├── invoice_qc/ │ ├── init.py │ ├── cli.py # CLI interface (Typer) │ ├── api.py # RESTful API interface (FastAPI) │ ├── schemas.py # Pydantic models for data │ ├── extractor.py # PDF parsing logic │ └── validator.py # Business and accounting rules ├── pdfs/ # Sample input PDFs ├── requirements.txt └── README.md


### System Flow

---

## 5. Setup & Installation

### Prerequisites

* [cite_start]**Python 3.9+** [cite: 1]
* [cite_start]Sample invoice PDFs placed inside the `/pdfs/` directory[cite: 1].

### Steps

1.  **Clone Repository (Updated Link):**
    ```bash
    git clone [https://github.com/Antaryami-044/invoice-qc-service-Assignment.git](https://github.com/Antaryami-044/invoice-qc-service-Assignment.git)
    cd invoice-qc-service-Assignment
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv venv
    
    # Linux/macOS
    source venv/bin/activate
    
    # Windows
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 6. Usage

### 6.1 CLI Commands

[cite_start]Run from the project root directory[cite: 1].

| Command | Description | Example |
| :--- | :--- | :--- |
| **Full Run** (Extract + Validate) | [cite_start]Processes PDFs and generates a QC report[cite: 1]. | [cite_start]`python -m invoice_qc.cli full-run --pdf-dir pdfs --report report.json` [cite: 1] |
| **Extract Only** | [cite_start]Converts PDFs to structured JSON data[cite: 1]. | [cite_start]`python -m invoice_qc.cli extract --pdf-dir pdfs --output data.json` [cite: 1] |
| **Validate Only** | [cite_start]Validates an existing JSON file[cite: 1]. | [cite_start]`python -m invoice_qc.cli validate --input data.json --report report_only.json` [cite: 1] |

### 6.2 HTTP API (FastAPI)

1.  **Run Server:**
    ```bash
    uvicorn invoice_qc.api:app --reload
    ```
    [cite_start]Documentation available at: `http://127.0.0.1:8000/docs`[cite: 1].

2.  **Health Check Example:**
    ```bash
    curl -X GET "[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)"
    # Expected response: {"status": "ok", "message": "Invoice QC Service is running."}
    ```

3.  **Validate JSON Example (POST):**
    ```bash
    curl -X POST "[http://127.0.0.1:8000/validate-json](http://127.0.0.1:8000/validate-json)" \
         -H "Content-Type: application/json" \
         -d @extracted_invoices.json
    ```

---

## 7. AI Usage Notes

[cite_start]The development process utilized large language models (LLMs) to ensure architectural best practices and efficiency[cite: 1].

| Tool Used | Primary Roles | Example Correction/Refinement |
| :--- | :--- | :--- |
| [cite_start]**Gemini (LLM)** [cite: 1] | [cite_start]Architectural validation [cite: 1][cite_start], Regex + parsing optimization[cite: 1]. | [cite_start]Avoiding blocking I/O in FastAPI[cite: 1]. |
| [cite_start]**GitHub Copilot** [cite: 1] | [cite_start]Boilerplate generation (CLI & API)[cite: 1]. | [cite_start]AI initially proposed synchronous file upload handling, which was updated to **async (await file.read())** for scalability[cite: 1]. |

---

## 8. Assumptions & Limitations

* [cite_start]Extraction relies heavily on **regex** tuned specifically for the sample PDFs provided[cite: 1].
* [cite_start]Table parsing may fail on highly complex or multiline layout invoices[cite: 1].
* [cite_start]The system is stateless; there is **no database** or historical Quality Control tracking[cite: 1].
* [cite_start]Line-item extraction is optimized for simple, standard column layouts[cite: 1].

---

## 9. Video Explanation

**Video Link:**
[YOUR\_VIDEO\_LINK]