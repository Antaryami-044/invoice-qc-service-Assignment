from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional

# Line Item Schema
class LineItem(BaseModel):
    description: str
    quantity: float = Field(ge=0)
    unit_price: float = Field(ge=0)
    line_total: float = Field(ge=0)

# invoice Schema 
class ExtractedInvoice(BaseModel):
    # Identifiers
    invoice_id: str
    invoice_number: Optional[str] = None
    
    # Dates
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    
    # Parties
    seller_name: Optional[str] = None
    seller_tax_id: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_tax_id: Optional[str] = None
    
    # Money
    currency: Optional[str] = None
    net_total: Optional[float] = None
    tax_amount: Optional[float] = None
    gross_total: Optional[float] = None
    
    # Line Items
    line_items: List[LineItem] = Field(default_factory=list)

# --- Validation Result Schemas ---
class ValidationResult(BaseModel):
    invoice_id: str
    is_valid: bool = True
    errors: List[str] = Field(default_factory=list)

class ValidationSummary(BaseModel):
    total_invoices: int
    valid_invoices: int
    invalid_invoices: int
    error_counts: dict
    results: List[ValidationResult]