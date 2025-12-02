"""
Form Filler Tool - Fills PDF forms with extracted information
"""
import os
import re
from typing import Dict, Any, Optional
from google.adk.tools import FunctionTool
from pypdf import PdfReader, PdfWriter
import json


def extract_info_from_post(post_text: str, linkedin_url: str) -> Dict[str, Any]:
    """
    Extracts information from LinkedIn post text using LLM-like pattern matching.
    In production, this would use Gemini to extract structured data.
    """
    info = {
        "name": "Worker",  # Default, would extract from post
        "address": "123 Main St, City, ST 12345",  # Default
        "last_employer": "Previous Employer",  # Would extract from post
        "last_wage": "50000",  # Would extract from post
        "email": None,  # Would need to be provided or extracted
        "phone": None,
        "linkedin_url": linkedin_url
    }
    
    # Simple extraction patterns (in production, use LLM)
    # Extract employer name
    employer_patterns = [
        r"(?:worked at|employed by|at)\s+([A-Z][a-zA-Z\s&]+?)(?:\s|,|\.|$)",
        r"(?:formerly|ex-)\s*([A-Z][a-zA-Z\s&]+)",
    ]
    
    for pattern in employer_patterns:
        match = re.search(pattern, post_text, re.IGNORECASE)
        if match:
            info["last_employer"] = match.group(1).strip()
            break
    
    # Extract salary/wage hints
    wage_patterns = [
        r"\$(\d{1,3}(?:,\d{3})*(?:k|K)?)",
        r"(\d{1,3}(?:,\d{3})*)\s*(?:per year|annually|salary)",
    ]
    
    for pattern in wage_patterns:
        match = re.search(pattern, post_text, re.IGNORECASE)
        if match:
            wage_str = match.group(1).replace(',', '')
            if 'k' in wage_str.lower():
                info["last_wage"] = str(int(float(wage_str.lower().replace('k', '')) * 1000))
            else:
                info["last_wage"] = wage_str
            break
    
    return info


def fill_pdf_form(
    pdf_path: str,
    output_path: str,
    form_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fills a PDF form with provided data.
    
    Args:
        pdf_path: Path to blank PDF form
        output_path: Path to save filled PDF
        form_data: Dictionary with form field names and values
    
    Returns:
        Dictionary with status and output path
    """
    try:
        if not os.path.exists(pdf_path):
            return {
                "status": "error",
                "message": f"PDF file not found: {pdf_path}"
            }
        
        # Read PDF
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Copy pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Fill form fields if PDF has form fields
        if reader.metadata:
            # Try to update form fields
            if hasattr(reader, 'get_form_text_fields'):
                form_fields = reader.get_form_text_fields()
                if form_fields:
                    for field_name, value in form_data.items():
                        # Map common field names
                        field_mapping = {
                            "name": ["name", "full_name", "applicant_name"],
                            "address": ["address", "street_address", "mailing_address"],
                            "employer": ["employer", "last_employer", "previous_employer"],
                            "wage": ["wage", "salary", "last_wage", "annual_wage"],
                            "email": ["email", "email_address"],
                            "phone": ["phone", "phone_number", "telephone"]
                        }
                        
                        # Find matching field
                        for key, aliases in field_mapping.items():
                            if key in field_name.lower():
                                for alias in aliases:
                                    if alias in form_fields:
                                        writer.update_page_form_field_values(
                                            reader.pages[0], {alias: str(value)}
                                        )
                                        break
        
        # Save filled PDF
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return {
            "status": "success",
            "output_path": output_path,
            "message": f"PDF filled and saved to {output_path}"
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error filling PDF: {str(e)}"
        }


def form_filler_tool(
    pdf_path: str,
    output_path: str,
    name: str,
    address: str,
    employer: str,
    wage: str,
    email: Optional[str] = None,
    phone: Optional[str] = None
) -> Dict[str, Any]:
    """
    ADK Tool wrapper for filling PDF forms.
    
    Args:
        pdf_path: Path to blank PDF form
        output_path: Path to save filled PDF
        name: Full name
        address: Full address
        employer: Last employer name
        wage: Last annual wage
        email: Email address (optional)
        phone: Phone number (optional)
    
    Returns:
        Dictionary with status and output path
    """
    form_data = {
        "name": name,
        "address": address,
        "employer": employer,
        "wage": wage,
    }
    
    if email:
        form_data["email"] = email
    if phone:
        form_data["phone"] = phone
    
    return fill_pdf_form(pdf_path, output_path, form_data)


# Create ADK Tool wrapper
# FunctionTool automatically extracts name and description from the function docstring and signature
form_filler_adk_tool = FunctionTool(form_filler_tool)

