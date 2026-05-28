# 🛡️ HideX - Secure PII Guard

A full-stack Python application that detects, classifies, and prevents leakage of government-issued Personally Identifiable Information (PII) from documents and text data.

## 🚀 Features
- **PII Detection**: Detects Aadhaar, PAN, Passport, Voter ID, Email, and Phone.
- **OCR Support**: Extracts text from PDF, DOCX, and Images (JPG, PNG).
- **Masking**: Automatically redacts sensitive information (e.g., `XXXX XXXX 9012`).
- **Audit Logs**: Stores scan history in MongoDB for compliance.
- **Interactive UI**: Modern Streamlit dashboard for real-time analysis.

## 🛠️ Tech Stack
- **Backend**: FastAPI, Python 3.9+
- **Frontend**: Streamlit
- **Database**: MongoDB
- **OCR**: Tesseract OCR, PDFPlumber, Python-DOCX
- **NLP**: SpaCy

## 📋 Prerequisites
1. **Python 3.9+**
2. **MongoDB**: Running locally or a cloud instance.
3. **Tesseract OCR**: Install on your system and add to PATH.
   - Windows: [Download here](https://github.com/UB-Mannheim/tesseract/wiki)
   - Linux: `sudo apt install tesseract-ocr`

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone <repo-url>
cd Blockchain-Government-PII
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
MONGO_URI=mongodb://localhost:27017
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe (if on Windows)
```

### 4. Run the Application

**Start the Backend:**
```bash
python -m backend.main
```

**Start the Frontend:**
```bash
streamlit run frontend/main.py
```

## 📄 API Documentation
- Once the backend is running, visit: `http://localhost:8000/docs`

## 🛡️ Security Features
- Regex-based high-accuracy detection.
- Hybrid NLP layer for context awareness.
- Secure temporary file handling.
- Sanitized file download capability.

---
Created for SIH / Hackathon / Placement Project.
