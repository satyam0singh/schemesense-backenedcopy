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
        Uses Gemini 2.5 (2026 standard) to extract structured scheme data.
        Includes robust fallback (2.5-flash -> 2.5-pro -> 2.0-flash).
        """
        if not GEMINI_API_KEY:
            return self._get_error_response("Gemini API Key missing in environment.")
        
        if not text:
            return self._get_error_response("No text could be extracted from the PDF.")

        # Try 2026-standard model names in order of preference
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.5-flash-latest",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-1.5-flash" # Legacy fallback
        ]
        
        last_error = ""
        for model_name in models_to_try:
            try:
                print(f"DEBUG: Attempting 2026 extraction with model: {model_name}")
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
                  "eligibility": "Detailed criteria...",
                  "benefits": "Key financial or service benefits...",
                  "documents": ["list", "of", "docs"],
                  "state": "Specific state or All States",
                  "official_link": "URL",
                  "confidence": "high/medium/low"
                }}
                
                Ensure no extra text, markdown formatting blocks, or dialogue. Return raw JSON string.
                """
                
                response = model.generate_content(prompt)
                
                # Robust cleaning of JSON response (strips markdown backticks)
                content = response.text.strip()
                content = re.sub(r'^```json\s*', '', content)
                content = re.sub(r'^```\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
                content = content.strip()
                
                # Parse and validate
                structured_data = json.loads(content)
                print(f"SUCCESS: Extracted data using 2026-model: {model_name}")
                return structured_data
                
            except Exception as e:
                last_error = str(e)
                print(f"DEBUG: Model {model_name} failed: {last_error}")
                # Continue loop to next model in case of 404/403/etc
                continue

        # Final failure check - List all models to diagnostics if all tried names failed
        available = []
        try:
             available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        except:
             pass
             
        error_msg = f"All models failed in 2026 context. Last model {model_name} error: {last_error}. "
        if available:
             error_msg += f"Available methods to your key: {', '.join(available)}"

        return self._get_error_response(error_msg)

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
        # 1. Extract raw text
        raw_text = self.extract_text_from_pdf(file_bytes)
        
        # 2. LLM Parse with Gemini 2.5
        result = self.parse_scheme_with_llm(raw_text)
        
        return result

pdf_parser_agent = PDFParserAgent()
