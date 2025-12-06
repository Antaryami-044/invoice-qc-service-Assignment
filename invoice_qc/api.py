from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import json
from io import BytesIO
import pdfplumber

from .schemas import ExtractedInvoice, ValidationSummary, ValidationResult
from .validator import run_validation
from .extractor import extract_data_from_pdf
from tempfile import NamedTemporaryFile
from pathlib import Path

app = FastAPI(
    title="Invoice QC Service API",
    description="API for validating extracted invoice data.",
    version="1.0.0"
)

# --- Endpoints ---

@app.get("/health", tags=["System"])
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Invoice QC Service is running."}

@app.post("/validate-json", response_model=ValidationSummary, tags=["Validation"])
async def validate_json_endpoint(
    invoices: List[ExtractedInvoice]
):
    """
    Validates a list of extracted invoice JSON objects against defined business rules.
    """
    # run_validation takes a list of ExtractedInvoice objects
    summary = run_validation(invoices)
    return summary

@app.post("/extract-and-validate-pdfs", response_model=ValidationSummary, tags=["Extraction & Validation"])
async def extract_and_validate_pdfs_endpoint(
    files: List[UploadFile] = File(..., description="List of PDF files to upload.")
):

    extracted_invoices: List[ExtractedInvoice] = []

    for file in files:
        if file.content_type != "application/pdf":
            # For a production system, you might want to log this but continue
            raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a PDF.")

        # FastAPI passes files as SpooledTemporaryFile; we need to save/access the content
        # For simplicity and to use the existing pdfplumber/Path logic:
        # Save to a temporary file
        try:
            with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = Path(tmp.name)
            
            # Use the existing extraction logic
            extracted_invoice = extract_data_from_pdf(tmp_path)
            # Override the invoice_id with the original filename for user clarity
            extracted_invoice.invoice_id = file.filename 
            extracted_invoices.append(extracted_invoice)
        finally:
            # Clean up the temporary file
            if 'tmp_path' in locals() and tmp_path.exists():
                tmp_path.unlink()


    if not extracted_invoices:
        raise HTTPException(status_code=400, detail="No valid PDFs were processed.")
        
    # Run Validation
    summary = run_validation(extracted_invoices)
    return summary