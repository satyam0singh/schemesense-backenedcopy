import io
import os
import json
from pypdf import PdfReader
import google.generativeai as genai

# Setup Gemini with API key from environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class PDFParserAgent:
    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """
        Extracts up to the first 4000 characters from a PDF file.
        Cleans newlines and redundant spaces.
        """
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + " "
                if len(text) > 4000:
                    break
            
            # Clean and limit
            cleaned_text = " ".join(text.replace("\n", " ").split())
            return cleaned_text[:4000]
        except Exception as e:
            print(f"Error extracting PDF text: {str(e)}")
            return ""

    def parse_scheme_with_llm(self, text: str) -> dict:
        """
        Uses Gemini 1.5 Flash to extract structured scheme data from raw text.
        """
        if not GEMINI_API_KEY:
            return self._get_error_response("Gemini API Key missing in environment.")
        
        if not text:
            return self._get_error_response("No text could be extracted from the PDF.")

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Extract the following fields from this government scheme document:
            
            - Scheme Name
            - Eligibility Criteria
            - Benefits
            - Required Documents (as list)
            - Target State
            - Official Website (if present)
            
            Scheme text:
            {text}
            
            Return STRICT JSON only in this exact format:
            {{
              "name": "Scheme name",
              "eligibility": "Fuzzy criteria...",
              "benefits": "List of benefits...",
              "documents": ["doc1", "doc2"],
              "state": "Name of state or All India",
              "official_link": "URL",
              "confidence": "high/medium/low"
            }}
            
            Ensure no extra text, markdown formatting blocks, or dialogue. Return raw JSON string.
            """
            
            response = model.generate_content(prompt)
            
            # Clean response text in case Gemini wraps it in ```json ... ```
            content = response.text.replace("```json", "").replace("```", "").strip()
            
            # Parse and validate
            structured_data = json.loads(content)
            return structured_data
            
        except Exception as e:
            print(f"LLM Extraction Error: {str(e)}")
            return self._get_error_response(f"Failed to extract structured data: {str(e)}")

    def _get_error_response(self, message: str) -> dict:
        return {
            "name": "Error",
            "eligibility": "N/A",
            "benefits": "N/A",
            "documents": [],
            "state": "N/A",
            "official_link": "",
            "confidence": "low",
            "error": message
        }

    def pdf_parser_agent(self, file_bytes: bytes) -> dict:
        """
        Main orchestration function for PDF extraction.
        """
        # 1. Extract
        raw_text = self.extract_text_from_pdf(file_bytes)
        
        # 2. LLM Parse
        result = self.parse_scheme_with_llm(raw_text)
        
        return result

pdf_parser_agent = PDFParserAgent()
