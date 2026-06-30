import json
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables (such as GEMINI_API_KEY)
load_dotenv()

# Define the Pydantic schema for individual audit items
class AuditItem(BaseModel):
    item: str
    category: str
    amount: float
    status: str
    reason: str

# Define the container schema for the audit report
class AuditReport(BaseModel):
    results: list[AuditItem]

# Initialize the GenAI client natively
import os
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))

def run_conversational_audit(narrative_text: str) -> list:
    """
    Processes an unstructured expense narrative, runs it through a 4-stage
    internal auditing pipeline, and returns the audited records as a list of dicts.
    """
    system_instruction = (
        "You are an expert Conversational Enterprise Expense Auditor. You must process "
        "the input text by executing a strict 4-stage internal pipeline:\n\n"
        "1. SEQUENTIAL AGENT (NER Extractor):\n"
        "   - Read the user's unstructured conversational text.\n"
        "   - Dynamically extract every distinct expense item.\n"
        "   - Map its title ('item') and dollar amount ('amount').\n"
        "   - Classify its category strictly into one of: 'Meals', 'Software', or 'Travel'.\n\n"
        "2. LOOP AGENT:\n"
        "   - Iterate deterministically, item-by-item, through all extracted records from Stage 1.\n\n"
        "3. AUDITOR AGENT:\n"
        "   - Evaluate each item's amount against corporate policy thresholds:\n"
        "     * Meals: Max $50.00\n"
        "     * Software: Max $100.00\n"
        "     * Travel: Max $500.00\n"
        "   - Flag status strictly as 'APPROVED' (if within/equal to threshold) or 'VIOLATION' (if exceeding threshold).\n"
        "   - Provide a clear, concise reason justifying the status (e.g., 'Within limit of $50.00' or 'Exceeds limit of $500.00 by $120.00').\n\n"
        "4. REPORTING AGENT:\n"
        "   - Compile the final state payload into the exact structure required by the Pydantic schema."
    )

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "results": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "item": {"type": "STRING"},
                        "category": {"type": "STRING"},
                        "amount": {"type": "NUMBER"},
                        "status": {"type": "STRING"},
                        "reason": {"type": "STRING"},
                    },
                    "required": ["item", "category", "amount", "status", "reason"],
                }
            }
        },
        "required": ["results"],
    }

    # Configure the generation call to guarantee structured JSON output matching AuditReport
    config = genai.types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.0,
        response_mime_type="application/json",
        response_schema=response_schema,
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=narrative_text,
        config=config,
    )

    # Parse and return the results as a list of dictionaries
    try:
        data = json.loads(response.text)
        return data.get("results", [])
    except Exception:
        return []
