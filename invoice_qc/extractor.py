import re
import pdfplumber
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from .schemas import ExtractedInvoice, LineItem, LineItem

# --- 1. Regex Patterns (CRITICAL: FINAL AGGRESSIVE VERSION) ---
PATTERNS = {
    # Order/Invoice Number: Capture the number following 'Bestellung' or 'AUFNR'
    "invoice_number": r"(?:Bestellung|AUFNR|Ref\.|Best\.)[:\W\s]*([A-Za-z0-9-]+)",
    
    # Date: Capture the date following 'vom' (from) or 'Bestelldatum'
    "invoice_date": r"(?:vom|Bestelldatum|Datum)[:\W\s]*(\d{1,4}[./-]\d{1,2}[./-]\d{2,4})",
    "due_date": r"(?:Zahlungsbedingungen|Lieferdatum|Fälligkeit)[:\W\s]*(\d{1,4}[./-]\d{1,2}[./-]\d{2,4})",
    
    # Seller Name: We use two patterns to capture one of the two corporation names
    "seller_name_pat1": r"^(ABC|ERT|JKL|BMN|XYZ)\s*Corporation",
    "seller_name_pat2": r"(?:medical\s*equipment|Mining\s*Equip|Unternehmen\s*für\s*Computerteile|Supplies\s*Equip)\s*\(Deutschland\)\s*(?:GmbH)?",
    
    # Monetary Fields: Capture the entire monetary block for cleaning
    # Aggressive pattern to capture money fields that appear near the summary labels
    "gross_total_label": r"Gesamtwert\s*inkl\.\s*MwSt\s*\W*([A-Z€£₹\s]*[\d\.,\s]*\d{2})",
    "net_total_label": r"Gesamtwert\s*\"EUR\"[\s\W]*([\d\.,\s]*\d{2})",
    "tax_amount_label": r"(?:MwSt|USt|VAT)[\s\d,\.%]*\W*([A-Z€£₹\s]*[\d\.,\s]*\d{2})",
    
    # Other Fields
    "buyer_name": r"Kundenanschrift\s*([A-Za-z\s,.]+)",
    "buyer_tax_id": r"(?:Kundennummer|Kunden-Nr|Endkundennummer)[:\W\s]*([A-Za-z0-9\-\/]+)",
}

# --- 2. Data Cleaning and Parsing Functions ---

def _clean_amount_and_currency(text: str) -> tuple[Optional[str], Optional[float]]:
    """
    Extracts currency code/symbol and float amount from text, standardizing formats
    (handles German/Euro format: 1.080,00 -> 1080.00).
    """
    if not text:
        return None, None
        
    text = text.replace(' ', '').strip()
    currency = None
    amount = None

    # HEURISTIC: If text ends with comma + two digits (e.g., 1.080,00), assume German format.
    if re.search(r"\.\d{3},\d{2}$", text) or re.search(r",\d{2}$", text):
        text = text.replace('.', '').replace(',', '.')
    # Otherwise, assume standard format (remove commas as thousand separators)
    else:
        text = text.replace(',', '')

    # Pattern to find a number which may have a leading currency symbol/code
    match = re.search(r"([A-Z]{3}|[€$£₹])?\s*([\d.]+)", text, re.IGNORECASE)
    
    if match:
        currency_raw = match.group(1) if match.group(1) else None
        amount_raw = match.group(2)
        
        if currency_raw:
            currency = currency_raw.upper().replace('€', 'EUR').replace('£', 'GBP').replace('₹', 'INR').replace('$', 'USD')
        
        try:
            amount = float(amount_raw)
        except ValueError:
            return None, None
    
    if not currency and "EUR" in text.upper():
         currency = "EUR"

    return currency, amount

def _parse_date(date_str: str) -> Optional[datetime.date]:
    """Tries to parse a date string into a date object, prioritizing common German/Euro formats."""
    if not date_str:
        return None
    formats = ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m-%d-%Y', '%d.%m.%y'] 
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

# --- 3. Line Item Extraction ---

def _extract_line_items(pdf_path: Path, full_text: str) -> List[LineItem]:
    """
    Extracts table data tuned for German headers ('Artikelbeschreibung' and 'Bestellwert').
    """
    line_items: List[LineItem] = []
    
    HEADER_TERMS = ['artikelbeschreibung', 'bestellwert', 'preis', 'menge']
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            
            for table in tables:
                if not table or not table[0]:
                    continue
                    
                header = [str(h).strip().lower().split('\n')[0] for h in table[0] if h]
                
                if not any(term in h for h in header for term in HEADER_TERMS):
                    continue
                
                col_map = {
                    'description': None, 
                    'quantity': None,    
                    'unit_price': None,  
                    'line_total': None   
                }
                
                for idx, col_name in enumerate(header):
                    if 'artikelbeschreibung' in col_name:
                        col_map['description'] = idx
                    elif 'menge' in col_name:
                        col_map['quantity'] = idx
                    elif 'preis' in col_name:
                        col_map['unit_price'] = idx
                    elif 'bestellwert' in col_name:
                        col_map['line_total'] = idx

                # Process rows, skipping the header row
                for row in table[1:]:
                    if not any(str(c).strip() for c in row): 
                        continue
                        
                    # Skip summary lines that are part of the table footer
                    if len(row) < 3 and any("EUR" in str(c).upper() for c in row):
                        continue

                    try:
                        desc = str(row[col_map['description']]).strip() if col_map.get('description') is not None and len(row) > col_map['description'] and row[col_map['description']] is not None else ""
                        qty_raw = str(row[col_map['quantity']]).split(' ')[0].strip() if col_map.get('quantity') is not None and len(row) > col_map['quantity'] and row[col_map['quantity']] is not None else "1.0"
                        unit_price_raw = str(row[col_map['unit_price']]).strip() if col_map.get('unit_price') is not None and len(row) > col_map['unit_price'] and row[col_map['unit_price']] is not None else "0.0"
                        line_total_raw = str(row[col_map['line_total']]).strip() if col_map.get('line_total') is not None and len(row) > col_map['line_total'] and row[col_map['line_total']] is not None else "0.0"

                        # Clean and convert to float
                        _, qty = _clean_amount_and_currency(qty_raw)
                        _, unit_price = _clean_amount_and_currency(unit_price_raw)
                        _, line_total = _clean_amount_and_currency(line_total_raw)
                        
                        if desc and line_total is not None and line_total > 0:
                            line_items.append(LineItem(
                                description=desc.replace('\n', ' '),
                                quantity=qty if qty is not None else 1.0,
                                unit_price=unit_price if unit_price is not None else 0.0,
                                line_total=line_total
                            ))
                            
                    except Exception:
                        continue

    return line_items

# --- 4. Main Extraction Function ---

def extract_data_from_pdf(pdf_path: Path) -> ExtractedInvoice:
    """Reads PDF, extracts text, and attempts to parse structured data."""
    
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "".join(page.extract_text() + "\n" for page in pdf.pages)
    except Exception as e:
        print(f"Error opening/reading PDF {pdf_path.name}: {e}")
        return ExtractedInvoice(invoice_id=pdf_path.name) 

    data: Dict[str, Any] = {"invoice_id": pdf_path.name}
    extracted_currency: Optional[str] = None

    # 1. Extract Core Fields using regex
    for field, pattern in PATTERNS.items():
        # Use re.DOTALL to allow matches across line breaks (CRITICAL FIX)
        match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL) 
        if match:
            # Handle specific multi-group/multi-pattern seller name matches
            if field in ["seller_name_pat1", "seller_name_pat2"]:
                value = match.group(0).strip()
                if not data.get("seller_name"):
                    data["seller_name"] = value
                continue
                
            # Assume group 1 captures the value for standard patterns
            try:
                raw_value = match.group(1).strip()
            except IndexError:
                raw_value = match.group(0).strip()

            if field.endswith("_label"):
                currency, amount = _clean_amount_and_currency(raw_value)
                
                if amount is not None:
                    if "gross_total" in field:
                        data["gross_total"] = amount
                    elif "net_total" in field:
                        data["net_total"] = amount
                    elif "tax_amount" in field:
                        data["tax_amount"] = amount
                
                if currency is not None and extracted_currency is None:
                    extracted_currency = currency
                    
            elif field.endswith("_date"):
                parsed_date = _parse_date(raw_value)
                if parsed_date:
                    data[field] = parsed_date
            else:
                data[field] = raw_value.replace('\n', ' ').strip()
                
    # 2. Extract Line Items 
    data["line_items"] = _extract_line_items(pdf_path, full_text)
    
    # 3. Finalize Currency 
    data["currency"] = extracted_currency if extracted_currency else "EUR" 

    # 4. Instantiate Pydantic model
    try:
        return ExtractedInvoice(**data)
    except Exception as e:
        print(f"Pydantic Validation/Type Error for {pdf_path.name}: {e}")
        return ExtractedInvoice(**{"invoice_id": pdf_path.name, **data})

def run_extraction(pdf_dir: Path) -> List[ExtractedInvoice]:
    """Extracts data from all PDFs in a directory."""
    invoices: List[ExtractedInvoice] = []
    
    if not pdf_dir.is_dir():
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

    for pdf_path in pdf_dir.glob("*.pdf"):
        if pdf_path.name.startswith('~'):
             continue 
             
        print(f"Processing: {pdf_path.name}")
        invoices.append(extract_data_from_pdf(pdf_path))
        
    return invoices