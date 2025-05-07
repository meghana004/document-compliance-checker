import streamlit as st
import pandas as pd
from docx import Document
import fitz  # PyMuPDF

# Function to read document
def read_document(file):
    text = ""
    if file.name.endswith('.docx'):
        doc = Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif file.name.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
    else:
        st.error("Unsupported file type! Please upload a .docx or .pdf file.")
    return text

# Function to check mandatory sections
def check_mandatory_sections(text, required_sections):
    results = []
    for section in required_sections:
        if section.lower() in text.lower():
            results.append({'Section': section, 'Status': '✅ Found'})
        else:
            results.append({'Section': section, 'Status': '❌ Not Found'})
    return results

# Function to check word count
def check_word_count(text, min_words=100, max_words=1000):
    word_count = len(text.split())
    if min_words <= word_count <= max_words:
        return word_count, "✅ OK"
    else:
        return word_count, "❌ Not OK"

# Function to calculate compliance score
def calculate_compliance_score(section_results, word_count_status):
    sections_passed = sum(1 for result in section_results if '✅' in result['Status'])
    total_sections = len(section_results)

    if word_count_status == "✅ OK":
        sections_passed += 1
    total_checks = total_sections + 1

    score = (sections_passed / total_checks) * 100
    passed = score >= 80

    return score, sections_passed, total_checks, passed

# Streamlit app starts here
st.title("📄 Document Compliance Checker")

uploaded_file = st.file_uploader("Upload your .docx or .pdf file", type=["docx", "pdf"])

if uploaded_file is not None:
    with st.spinner('Reading document...'):
        text = read_document(uploaded_file)

    mandatory_sections = ['Introduction', 'Objective', 'Skills', 'Education', 'Experience', 'Conclusion']

    section_results = check_mandatory_sections(text, mandatory_sections)
    word_count, word_status = check_word_count(text)
    score, passed_sections, total_checks, passed = calculate_compliance_score(section_results, word_status)

    # Show Results
    st.subheader("📋 Section Check Result")
    df = pd.DataFrame(section_results)
    st.dataframe(df)

    st.subheader("🧮 Word Count Check")
    st.write(f"Word Count: {word_count}")
    st.write(f"Status: {word_status}")

    st.subheader("📈 Final Compliance Score")
    st.write(f"Score: {score:.2f}%")
    if passed:
        st.success("✅ Document PASSED Compliance Check!")
    else:
        st.error("❌ Document FAILED Compliance Check!")
