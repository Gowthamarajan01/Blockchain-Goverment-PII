import streamlit as st
import requests
import pandas as pd
import json
import io
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="PII Shield - Government Data Protection",
    page_icon="🛡️",
    layout="wide",
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .pii-card {
        padding: 1.5rem;
        border-radius: 15px;
        background: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border-left: 5px solid #007bff;
    }
    .high-risk { border-left-color: #dc3545; }
    .medium-risk { border-left-color: #ffc107; }
    .low-risk { border-left-color: #28a745; }
    
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-safe { background-color: #d4edda; color: #155724; }
    .status-alert { background-color: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# API URL
API_URL = "http://127.0.0.1:8000"

def main():
    st.title("🛡️ PII Shield")
    st.subheader("Government-Issued Personally Identifiable Information Detector")
    
    tabs = st.tabs(["🔍 Scan Text/File", "📊 Audit Logs", "ℹ️ About"])
    
    with tabs[0]:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📝 Input Data")
            input_mode = st.radio("Choose Input Mode", ["Text Input", "File Upload"], horizontal=True)
            
            if input_mode == "Text Input":
                text_input = st.text_area("Paste text content here...", height=300, 
                                        placeholder="e.g. My Aadhaar is 1234 5678 9012 and PAN is ABCDE1234F")
                if st.button("Analyze Text"):
                    if text_input:
                        with st.spinner("Analyzing..."):
                            response = requests.post(f"{API_URL}/scan-text", json={"text": text_input})
                            if response.status_code == 200:
                                st.session_state['results'] = response.json()
                            else:
                                st.error("Failed to connect to backend.")
            else:
                uploaded_file = st.file_uploader("Upload Document (PDF, DOCX, JPG, PNG)", 
                                               type=["pdf", "docx", "jpg", "jpeg", "png", "txt"])
                if st.button("Scan Document"):
                    if uploaded_file:
                        with st.spinner("Processing file..."):
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            response = requests.post(f"{API_URL}/scan-file", files=files)
                            if response.status_code == 200:
                                st.session_state['results'] = response.json()
                            else:
                                st.error("Failed to process file.")

        with col2:
            st.markdown("### 🔬 Scan Results")
            if 'results' in st.session_state:
                res = st.session_state['results']
                pii_list = res.get('pii_found', [])
                
                if pii_list:
                    st.warning(f"⚠️ Found {len(pii_list)} sensitive information items!")
                    
                    for item in pii_list:
                        risk_class = "high-risk" if item['sensitivity'] == "High" else "medium-risk"
                        st.markdown(f"""
                        <div class="pii-card {risk_class}">
                            <b>Type:</b> {item['type']} <br>
                            <b>Value:</b> <code style='color:#d63384'>{item['value']}</code> <br>
                            <b>Confidence:</b> {item['confidence']*100}% | <b>Severity:</b> {item['sensitivity']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("### 🔒 Sanitized Output")
                    st.code(res['masked_text'], language="text")
                    
                    if res.get('saved_to'):
                        st.info(f"📂 Also saved to system at: `{res['saved_to']}`")
                    
                    # Download button
                    st.download_button(
                        label="Download Masked Content",
                        data=res['masked_text'],
                        file_name=f"sanitized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.success("✅ No sensitive PII detected. Content is safe.")
            else:
                st.info("Results will appear here after scanning.")

    with tabs[1]:
        st.markdown("### 📋 Audit Trail & Logs")
        if st.button("Refresh Logs"):
            try:
                response = requests.get(f"{API_URL}/logs")
                if response.status_code == 200:
                    logs = response.json()
                    if logs:
                        df = pd.DataFrame(logs)
                        st.table(df)
                    else:
                        st.write("No logs found.")
            except:
                st.error("Could not fetch logs.")

    with tabs[2]:
        st.markdown("""
        ### About PII Shield
        This application is designed to prevent the accidental leakage of sensitive government-issued PII.
        
        **Supported Identifiers:**
        - Aadhaar Number (12 Digit)
        - PAN Card Number
        - Passport Number
        - Voter ID (EPIC)
        - Contact Information (Phone, Email)
        
        **Technology Used:**
        - **FastAPI**: High-performance backend
        - **Streamlit**: Modern frontend
        - **SpaCy**: Natural Language Processing
        - **PyTesseract**: Optical Character Recognition
        - **MongoDB**: Secure logging
        """)

if __name__ == "__main__":
    main()
