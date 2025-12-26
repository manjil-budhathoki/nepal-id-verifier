import streamlit as st
import requests
from PIL import Image

# --- CONFIG ---
API_URL = "http://localhost:8000/verify"

st.set_page_config(page_title="ID Audit Pro", layout="wide")

st.title("🪪 ID Audit & Taxonomy Dashboard (FastAPI)")

# --- SIDEBAR ---
with st.sidebar:
    st.header("👤 Verification Entry")
    u_name = st.text_input("Full Name")
    u_id = st.text_input("Citizenship Number")
    u_dob = st.text_input("DOB (YYYY-MM-DD)")
    verify_btn = st.button("Run Audit Pipeline")

# --- MAIN UI ---
uploaded_file = st.file_uploader("Upload ID Document", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Show Preview
    st.image(uploaded_file, caption="Uploaded Document", width=400)

    if verify_btn:
        if not u_name or not u_id or not u_dob:
            st.error("Please fill in all User Details in the sidebar.")
        else:
            with st.spinner("⏳ Sending to Neural Engine..."):
                try:
                    # Prepare Payload
                    files = {"file": uploaded_file.getvalue()}
                    data = {
                        "name": u_name,
                        "id_number": u_id,
                        "dob": u_dob
                    }
                    
                    # Call FastAPI
                    response = requests.post(API_URL, files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        audit_report = result["report"]
                        tax_counts = result["taxonomy"]
                        ocr_data = result["ocr_details"]
                        
                        st.success("Analysis Complete!")
                        st.divider()
                        
                        # 1. SHOW REPORT
                        st.header("🏁 Deterministic Audit Report")
                        for field, data in audit_report.items():
                            with st.container(border=True):
                                c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
                                c1.write(f"**{field.upper()}**")
                                
                                # Status Color
                                color = "green" if data['status'] == "MATCH" else "orange" if data['status'] == "PARTIAL" else "red"
                                c2.markdown(f":{color}[**{data['status']}**]")
                                
                                c3.metric("Score", f"{data['score']}%")
                                
                                with c4:
                                    st.markdown(f"**Found:** `{data['span']}`")
                                    if data['score'] < 100:
                                        st.caption(f"Taxonomy: {data['error_type']}")

                        # 2. TAXONOMY DASHBOARD
                        st.markdown("### 📊 System Error Taxonomy")
                        tax_cols = st.columns(len(tax_counts) if tax_counts else 1)
                        for idx, (err, count) in enumerate(tax_counts.items()):
                            label_color = "white" if err == "SUCCESS" else "#ff4b4b"
                            tax_cols[idx].markdown(
                                f"<div style='border:1px solid #444; padding:10px; border-radius:5px; text-align:center;'>"
                                f"<span style='color:{label_color}; font-size:0.7rem;'>{err}</span><br>"
                                f"<span style='font-size:1.5rem; font-weight:bold;'>{count}</span>"
                                f"</div>", 
                                unsafe_allow_html=True
                            )
                        
                        # 3. DEBUG OCR DATA
                        with st.expander("See Raw OCR Data"):
                            st.json(ocr_data)

                    else:
                        st.error(f"Server Error: {response.text}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not connect to Backend. Is 'backend.py' running?")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")