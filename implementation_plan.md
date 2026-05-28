# Implementation Plan - Government PII Leakage Prevention System

## Project Overview
A full-stack Python application to detect, classify, and prevent leakage of Indian government-issued PII (Aadhaar, PAN, Passport, Voter ID) from documents and text.

## Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Database**: MongoDB
- **OCR/Extraction**: `pytesseract`, `pdfplumber`, `python-docx`
- **Detection**: Regex + NLP (spaCy)

## Phase 1: Foundation & Project Structure
1. Create directory structure:
   - `backend/`: FastAPI app, routes, services, models.
   - `frontend/`: Streamlit dashboard.
   - `models/`: Database models.
   - `utils/`: Common utilities.
   - `data/`: Temporary storage for processed files.
2. Initialize `requirements.txt`.

## Phase 2: Core PII Detection Service
1. Implement Regex-based patterns for:
   - Aadhaar: `\d{4}\s\d{4}\s\d{4}`
   - PAN: `[A-Z]{5}[0-9]{4}[A-Z]{1}`
   - Passport: `[A-Z][0-9]{7}`
   - Voter ID: `[A-Z]{3}[0-9]{7}` (standard format)
2. Implement basic spaCy NLP for name/entity recognition.
3. Implement confidence scoring logic.

## Phase 3: Extraction & Masking Services
1. **OCR Service**: Use `pytesseract` for images and PDFs with text-as-image.
2. **PDF Service**: Use `pdfplumber` for text-based PDFs.
3. **DOCX Service**: Use `python-docx`.
4. **Masking Service**: Replace detected strings with masked versions (e.g., `XXXX XXXX 9012`).

## Phase 4: Backend API Development (FastAPI)
1. Setup FastAPI entry point (`main.py`).
2. Implement Routes:
   - `POST /scan`: Handle file uploads and return detected PII.
   - `POST /mask`: Return redacted content.
   - `GET /logs`: Fetch scan history from MongoDB.
3. Implement JWT-based Auth (Basic).
4. MongoDB integration for logging.

## Phase 5: Frontend Development (Streamlit)
1. Build the main dashboard layout.
2. File upload component.
3. Real-time text input analyzer.
4. Results visualization (Highlighted PII, Sensitivity labels).
5. Masked output preview and File Download.

## Phase 6: Advanced Features & Refinement
1. Multi-language support (English/Tamil) - basic keyword mapping.
2. Batch processing UI.
3. Audit logs dashboard.
4. UI/UX Polishing with premium colors and animations.

## Phase 7: Deployment & Documentation
1. Create `README.md` with setup instructions.
2. Add sample test data.
