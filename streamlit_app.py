import streamlit as st
import requests
import os
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# CONFIG (Points to the new API path)
# -------------------------------------------------
API_BASE = os.getenv("API_URL", "http://localhost:8000")
API_VERIFY_URL = f"{API_BASE}/api/v1/verify"
API_HEALTH_URL = f"{API_BASE}/health"

st.set_page_config(page_title="ID Audit Pro [Production]", layout="wide")

st.title("🪪 ID Audit & Verification (Production Build)")

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.header("System Status")
    try:
        health = requests.get(API_HEALTH_URL, timeout=2).json()
        st.success(f"Backend: {health.get('status')} ({health.get('mode')})")
    except:
        st.error("Backend Offline")

    st.divider()
    st.header("👤 Verification Entry")
    u_name = st.text_input("Full Name")
    u_id = st.text_input("Citizenship Number")
    u_dob = st.text_input("DOB (YYYY-MM-DD)")
    verify_btn = st.button("🚀 Run Verification")

# -------------------------------------------------
# MAIN
# -------------------------------------------------
uploaded_file = st.file_uploader("Upload Citizenship Document", type=["jpg", "jpeg", "png"])

if uploaded_file and verify_btn:
    if not u_name or not u_id or not u_dob:
        st.error("Please fill all required fields.")
    else:
        st.image(uploaded_file, caption="Uploaded Document", width=400)

        with st.spinner("⏳ Processing via API v1..."):
            try:
                # Prepare Payload
                # Send (Filename, Bytes, MimeType) tuple
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                }
                data = {"name": u_name, "id_number": u_id, "dob": u_dob}

                # Send Request
                response = requests.post(API_VERIFY_URL, files=files, data=data, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    
                    # 1. Audit Report
                    st.divider()
                    st.header("🏁 Audit Report")
                    
                    report = result.get("report", {})
                    
                    # Create 3 columns for Name, ID, DOB
                    cols = st.columns(3)
                    fields = ["name", "id_number", "dob"]
                    
                    for i, field in enumerate(fields):
                        data = report.get(field, {})
                        with cols[i]:
                            st.subheader(field.upper().replace("_", " "))
                            
                            status = data.get("status", "UNKNOWN")
                            color = "green" if status == "MATCH" else "red"
                            st.markdown(f":{color}[**{status}**]")
                            
                            st.caption(f"Score: {data.get('score')}%")
                            st.info(f"Detected: {data.get('span')}")

                    # 2. OCR Debug Data
                    with st.expander("🔍 Developer Debug: OCR Output"):
                        ocr_data = result.get("ocr_details", [])
                        if ocr_data:
                            df = pd.DataFrame(ocr_data)
                            # Clean up dataframe for display
                            st.dataframe(df)
                        else:
                            st.warning("No OCR data returned.")

                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")

            except Exception as e:
                st.error(f"Connection Failed: {e}")