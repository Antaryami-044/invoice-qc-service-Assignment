import json
import typer
from pathlib import Path
from typing import Optional
from .extractor import run_extraction
from .validator import run_validation
from .schemas import ExtractedInvoice, ValidationSummary

app = typer.Typer()

def _print_summary(summary: ValidationSummary):
    """Prints a human-readable summary to stdout."""
    typer.echo("--- QC SERVICE SUMMARY ---")
    typer.echo(f"Total Invoices: {summary.total_invoices}")
    typer.echo(f"Valid Invoices: {summary.valid_invoices}")
    typer.echo(f"Invalid Invoices: {summary.invalid_invoices}")
    typer.echo("--------------------------")
    if summary.invalid_invoices > 0:
        typer.echo("Top Errors:")
        # Sort errors by count
        sorted_errors = sorted(summary.error_counts.items(), key=lambda item: item[1], reverse=True)
        for error, count in sorted_errors:
            typer.echo(f"- {error}: {count} occurrences")
    typer.echo("--------------------------")


@app.command(name="extract", help="Extracts structured data from a directory of PDFs.")
def extract_cmd(
    pdf_dir: Path = typer.Option(..., "--pdf-dir", help="Directory containing PDF invoices."),
    output: Path = typer.Option("extracted_invoices.json", "--output", help="File to save extracted JSON."),
):
    """CLI command to run extraction only."""
    try:
        invoices = run_extraction(pdf_dir)
        
        # Save output JSON
        with open(output, "w") as f:
            # Use Pydantic's model_dump_json for easy serialization
            json_data = [inv.model_dump(mode='json') for inv in invoices]
            json.dump(json_data, f, indent=2)
            
        typer.echo(f"\nExtraction complete. Saved {len(invoices)} invoices to {output}")
        
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

@app.command(name="validate", help="Validates extracted JSON data against defined rules.")
def validate_cmd(
    input: Path = typer.Option(..., "--input", help="File containing extracted invoice JSON data."),
    report: Path = typer.Option("validation_report.json", "--report", help="File to save the validation report."),
):
    """CLI command to run validation only."""
    try:
        # Load input JSON
        with open(input, "r") as f:
            data = json.load(f)
            invoices = [ExtractedInvoice.model_validate(d) for d in data]
            
        summary = run_validation(invoices)
        
        # Save report JSON
        with open(report, "w") as f:
            json.dump(summary.model_dump(mode='json'), f, indent=2)

        _print_summary(summary)
        typer.echo(f"Validation complete. Saved report to {report}")

        if summary.invalid_invoices > 0:
            raise typer.Exit(code=2) # Non-zero exit code for invalid invoices
            
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
    except json.JSONDecodeError:
        typer.echo("Error: Invalid JSON input file.", err=True)
        raise typer.Exit(code=1)


@app.command(name="full-run", help="Runs extraction and validation end-to-end.")
def full_run_cmd(
    pdf_dir: Path = typer.Option(..., "--pdf-dir", help="Directory containing PDF invoices."),
    report: Path = typer.Option("validation_report.json", "--report", help="File to save the validation report."),
):
    typer.echo(f"--- Starting Full Run: {pdf_dir} ---")
    
    # Run Extraction
    try:
        invoices = run_extraction(pdf_dir)
    except FileNotFoundError as e:
        typer.echo(f"Extraction Error: {e}", err=True)
        raise typer.Exit(code=1)
        
    # Run Validation
    summary = run_validation(invoices)
    
    # Save Report
    with open(report, "w") as f:
        json.dump(summary.model_dump(mode='json'), f, indent=2)

    _print_summary(summary)
    typer.echo(f"Full Run Complete. Report saved to {report}")

    if summary.invalid_invoices > 0:
        raise typer.Exit(code=2) # Non-zero exit code for invalid invoices


if __name__ == "__main__":
    app()