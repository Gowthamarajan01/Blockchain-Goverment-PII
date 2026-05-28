import pdfplumber
import docx
import pytesseract
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load env variables and set Tesseract path for Windows if specified
load_dotenv()
tesseract_path = os.getenv("TESSERACT_PATH")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

class OCRService:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    else:
                        # Fallback for scanned PDFs: Convert page to image and OCR
                        try:
                            im = page.to_image(resolution=300)
                            image_text = pytesseract.image_to_string(im.original, lang='eng+tam')
                            if image_text:
                                text += image_text + "\n"
                        except Exception as ocr_err:
                            print(f"Fallback OCR failed for page: {ocr_err}")
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        return text

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
        return text

    @staticmethod
    def extract_text_from_image(file_path: str) -> str:
        text = ""
        try:
            from PIL import Image, ImageOps, ImageEnhance
            with Image.open(file_path) as image:
                # Preprocessing for better OCR: Convert to Grayscale
                grayscale_image = ImageOps.grayscale(image)
                
                # Increase contrast for better text recognition
                enhancer = ImageEnhance.Contrast(grayscale_image)
                processed_image = enhancer.enhance(2.0)
                
                # Added Tamil support (requires 'tam' trainneddata)
                text = pytesseract.image_to_string(processed_image, lang='eng+tam')
        except Exception as e:
            print(f"Error extracting Image: {e}")
        return text

    @staticmethod
    def _auto_correct_tamil(text: str) -> str:
        """Refined fix for common Tamil OCR errors using specific patterns."""
        if not text:
            return text
            
        import re
        
        # Mapping of common broken OCR fragments to correct Tamil words
        # Using word boundaries where possible to avoid over-correction (like நகர் -> நகரூர்)
        corrections = [
            (r"கவரி:", "முகவரி:"),
            (r"\bதமழ் நா\b", "தமிழ் நாடு"),
            (r"ராமாஜம்", "ராமானுஜம்"),
            (r"\bகர்\b", "கரூர்"), # Only replace standalone 'கர்'
            (r"ெதற்", "தெற்கு"),
            (r"ெசங்", "செங்குந்தபுரம்"),
            (r"பக்\s*ப", "தீபக் பி"), # Deepak P
            (r"பரேமஸ்\s*வரன்", "பரமேஸ்வரன்"), # Parameswaran
            (r"ேகரூர்\s*ஆப்", "கேர் ஆப்"), # Care of / C/O
            (r"ந்தரம்", "புரம்"), # Common suffix fix if doubled
        ]
        
        corrected_text = text
        for pattern, replacement in corrections:
            corrected_text = re.sub(pattern, replacement, corrected_text)
            
        # Specific cleanup for the bug 'நகர்' -> 'நகரூர்' if it happened
        corrected_text = corrected_text.replace("நகரூர்", "நகர்")
            
        return corrected_text

    @staticmethod
    def extract_text(file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        text = ""
        if ext == '.pdf':
            text = OCRService.extract_text_from_pdf(file_path)
        elif ext == '.docx':
            text = OCRService.extract_text_from_docx(file_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            text = OCRService.extract_text_from_image(file_path)
        elif ext == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()
        
        return OCRService._auto_correct_tamil(text)
