import io
import os
import json
import re
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
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
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
        Uses Gemini to extract structured scheme data from raw text.
        Includes model fallback for robustness (flash-latest -> pro).
        """
        if not GEMINI_API_KEY:
            return self._get_error_response("Gemini API Key missing in environment.")
        
        if not text:
            return self._get_error_response("No text could be extracted from the PDF.")

        # Try multiple model names in order of preference
        models_to_try = ["gemini-1.5-flash-latest", "gemini-1.5-flash", "gemini-pro"]
        
        last_error = ""
        for model_name in models_to_try:
            try:
                print(f"DEBUG: Attempting extraction with model: {model_name}")
                model = genai.GenerativeModel(model_name)
                
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
                
                # Robust cleaning of JSON response (strips markdown backticks)
                content = response.text.strip()
                # Remove Markdown code blocks if present
                content = re.sub(r'^```json\s*', '', content)
                content = re.sub(r'^```\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
                content = content.strip()
                
                # Parse and validate
                structured_data = json.loads(content)
                print(f"SUCCESS: Extracted data using {model_name}")
                return structured_data
                
            except Exception as e:
                last_error = str(e)
                print(f"DEBUG: Model {model_name} failed: {last_error}")
                # Continue loop to next model in case of 404/403/etc
                continue

        # If all models fail
        return self._get_error_response(f"All extraction models failed. Last error: {last_error}")

    def _get_error_response(self, message: str) -> dict:
        return {
            "name": "Extraction Error",
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
