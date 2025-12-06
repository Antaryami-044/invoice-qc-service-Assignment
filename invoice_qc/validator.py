# from typing import List, Dict, Any
# from datetime import date
# from .schemas import ExtractedInvoice, ValidationResult, ValidationSummary

# def validate_invoice(invoice: ExtractedInvoice, all_invoices: List[ExtractedInvoice]) -> ValidationResult:
#     """Applies all validation rules to a single extracted invoice."""
    
#     result = ValidationResult(invoice_id=invoice.invoice_id, is_valid=True, errors=[])
    
#     # --- RUL_001_CRITICAL_FIELDS (Completeness) ---
#     critical_fields = [
#         ("invoice_number", invoice.invoice_number), 
#         ("invoice_date", invoice.invoice_date), 
#         ("seller_name", invoice.seller_name), 
#         ("gross_total", invoice.gross_total)
#     ]
#     for field_name, value in critical_fields:
#         if value is None or (isinstance(value, str) and not value.strip()):
#             result.errors.append(f"RUL_001_CRITICAL_FIELDS: missing_field:{field_name}")

#     # --- RUL_002_KNOWN_CURRENCY (Format) ---
#     known_currencies = {"EUR", "USD", "INR", "GBP"}
#     if invoice.currency and invoice.currency.upper() not in known_currencies:
#         result.errors.append(f"RUL_002_KNOWN_CURRENCY: unknown_currency:{invoice.currency}")

#     # --- RUL_003_NON_NEGATIVE_TOTALS (Format) ---
#     for field_name, value in [("net_total", invoice.net_total), ("tax_amount", invoice.tax_amount), ("gross_total", invoice.gross_total)]:
#         if value is not None and value < 0:
#             result.errors.append(f"RUL_003_NON_NEGATIVE_TOTALS: negative_total:{field_name}")

#     # --- RUL_101_TOTALS_MATCH (Business Rule) ---
#     if invoice.gross_total is not None and invoice.net_total is not None and invoice.tax_amount is not None:
#         calculated_gross = invoice.net_total + invoice.tax_amount
#         # Allow a tiny margin for float comparison errors
#         if abs(invoice.gross_total - calculated_gross) > 0.01:
#             result.errors.append("RUL_101_TOTALS_MATCH: totals_mismatch")

#     # --- RUL_102_DUE_DATE_LOGIC (Business Rule) ---
#     if isinstance(invoice.due_date, date) and isinstance(invoice.invoice_date, date):
#         if invoice.due_date < invoice.invoice_date:
#             result.errors.append("RUL_102_DUE_DATE_LOGIC: due_date_before_invoice_date")
            
#     # --- RUL_201_LINE_TOTAL_SUM (Anomaly/Duplicate) ---
#     if invoice.net_total is not None and invoice.line_items:
#         line_item_sum = sum(item.line_total for item in invoice.line_items)
#         if abs(invoice.net_total - line_item_sum) > 0.01:
#             result.errors.append("RUL_201_LINE_TOTAL_SUM: net_total_line_item_sum_mismatch")
            
#     # Update final status
#     result.is_valid = not bool(result.errors)
#     return result

# def create_summary(results: List[ValidationResult]) -> ValidationSummary:
#     """Aggregates per-invoice results into a summary object."""
    
#     total_invoices = len(results)
#     valid_invoices = sum(1 for r in results if r.is_valid)
#     invalid_invoices = total_invoices - valid_invoices
    
#     error_counts: Dict[str, int] = {}
#     for r in results:
#         for error in r.errors:
#             # Clean error name for counting (e.g., just 'totals_mismatch')
#             clean_error = error.split(":")[-1].strip()
#             error_counts[clean_error] = error_counts.get(clean_error, 0) + 1
            
#     return ValidationSummary(
#         total_invoices=total_invoices,
#         valid_invoices=valid_invoices,
#         invalid_invoices=invalid_invoices,
#         error_counts=error_counts,
#         results=results
#     )

# def run_validation(invoices: List[ExtractedInvoice]) -> ValidationSummary:
#     """Runs validation on a list of invoices and creates a summary."""
#     # Note: Duplicate checking (e.g., same invoice_number + seller) 
#     # would require iterating over all_invoices inside validate_invoice. 
#     # For time, we skip that complex check, focusing on per-invoice rules.

#     results = [validate_invoice(inv, invoices) for inv in invoices]
#     return create_summary(results)







from typing import List, Dict, Any
from datetime import date
from .schemas import ExtractedInvoice, ValidationResult, ValidationSummary

def validate_invoice(invoice: ExtractedInvoice, all_invoices: List[ExtractedInvoice]) -> ValidationResult:
    """Applies all validation rules to a single extracted invoice."""
    
    result = ValidationResult(invoice_id=invoice.invoice_id, is_valid=True, errors=[])
    
    # --- RUL_001_CRITICAL_FIELDS (Completeness) ---
    critical_fields = [
        ("invoice_number", invoice.invoice_number), 
        ("invoice_date", invoice.invoice_date), 
        ("seller_name", invoice.seller_name), 
        ("gross_total", invoice.gross_total)
    ]
    for field_name, value in critical_fields:
        if value is None or (isinstance(value, str) and not value.strip()):
            result.errors.append(f"RUL_001_CRITICAL_FIELDS: missing_field:{field_name}")

    # Exit early if critical fields are missing to avoid confusing errors downstream
    if result.errors:
        result.is_valid = False
        return result

    # --- RUL_002_KNOWN_CURRENCY (Format) ---
    known_currencies = {"EUR", "USD", "INR", "GBP"}
    if invoice.currency and invoice.currency.upper() not in known_currencies:
        result.errors.append(f"RUL_002_KNOWN_CURRENCY: unknown_currency:{invoice.currency}")

    # --- RUL_003_NON_NEGATIVE_TOTALS (Format) ---
    for field_name, value in [("net_total", invoice.net_total), ("tax_amount", invoice.tax_amount), ("gross_total", invoice.gross_total)]:
        if value is not None and value < 0:
            result.errors.append(f"RUL_003_NON_NEGATIVE_TOTALS: negative_total:{field_name}")

    # --- RUL_101_TOTALS_MATCH (Business Rule: Net + Tax = Gross) ---
    if invoice.gross_total is not None and invoice.net_total is not None and invoice.tax_amount is not None:
        calculated_gross = invoice.net_total + invoice.tax_amount
        # Allow a tolerance of 1 cent (0.01) for float errors
        if abs(invoice.gross_total - calculated_gross) > 0.01:
            result.errors.append("RUL_101_TOTALS_MATCH: totals_mismatch")

    # --- RUL_102_DUE_DATE_LOGIC (Business Rule: Due date after invoice date) ---
    if isinstance(invoice.due_date, date) and isinstance(invoice.invoice_date, date):
        if invoice.due_date < invoice.invoice_date:
            result.errors.append("RUL_102_DUE_DATE_LOGIC: due_date_before_invoice_date")
            
    # --- RUL_201_LINE_TOTAL_SUM (Consistency: Line Sum = Net Total) ---
    if invoice.net_total is not None and invoice.line_items:
        line_item_sum = sum(item.line_total for item in invoice.line_items)
        # Allow a tolerance of 1 cent (0.01) for float errors
        if abs(invoice.net_total - line_item_sum) > 0.01:
            result.errors.append("RUL_201_LINE_TOTAL_SUM: net_total_line_item_sum_mismatch")
            
    # Update final status
    result.is_valid = not bool(result.errors)
    return result

def create_summary(results: List[ValidationResult]) -> ValidationSummary:
    """Aggregates per-invoice results into a summary object."""
    
    total_invoices = len(results)
    valid_invoices = sum(1 for r in results if r.is_valid)
    invalid_invoices = total_invoices - valid_invoices
    
    error_counts: Dict[str, int] = {}
    for r in results:
        for error in r.errors:
            # Clean error name for counting 
            clean_error = error.split(":")[-1].strip()
            error_counts[clean_error] = error_counts.get(clean_error, 0) + 1
            
    return ValidationSummary(
        total_invoices=total_invoices,
        valid_invoices=valid_invoices,
        invalid_invoices=invalid_invoices,
        error_counts=error_counts,
        results=results
    )

def run_validation(invoices: List[ExtractedInvoice]) -> ValidationSummary:
    """Runs validation on a list of invoices and creates a summary."""
    results = [validate_invoice(inv, invoices) for inv in invoices]
    return create_summary(results)