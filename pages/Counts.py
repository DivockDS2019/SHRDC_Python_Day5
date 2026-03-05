import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import plotly.express as px
import os
from PIL import Image as PILImage
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Counts", layout="wide")
st.title("Counts in COVID-19 Data")

df = pd.read_csv('dataset.csv')
dictionary = pd.read_excel('data_dictionary.xlsx')

df["SEX"] = df["SEX"].map({1:"FEMALE", 2:"MALE", 99:"UNKNOWN"})
df["OUTCOME"] = df["OUTCOME"].map({1:"POSITIVE", 2:"NEGTIVE", 3:"PENDING"})
df["COUNTRY OF ORIGIN"] = df["NATIONALITY"].map({1:"MEXICAN", 2:"FOREIGN", 99:"UNKNOWN"})
yn_map = {1:"YES", 2:"NO", 97:"DOES NOT APPLY", 98:"IGNORED", 99:"UNKNOWN"}

cols = [
"INTUBATED","PNEUMONIA","PREGNANCY", "SPEAKS_NATIVE_LANGUAGE","DIABETES","COPD","ASTHMA","INMUSUPR",
"HYPERTENSION","OTHER_DISEASE","CARDIOVASCULAR","OBESITY", "CHRONIC_KIDNEY","TOBACCO","ANOTHER CASE", "ICU", "MIGRANT"
]

for c in cols:
    df[c] = df[c].map(yn_map)

#-----------------------
# Q3 
#-----------------------

count_intubation = df['INTUBATED'].value_counts().get('YES', 0)

st.metric(label = "Number of people who required intubation", value = count_intubation)

st.dataframe(df)

def export_counts_to_pdf():
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # --- Add Logo ---
    logo_path = "shrdc_logo.png"
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=150, height=50))
        elements.append(Spacer(1, 20))

    # --- Title ---
    elements.append(Paragraph("COVID-19 Counts", styles["Heading1"]))
    elements.append(Spacer(1, 10))

    # --- Timestamp ---
    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 20))

    # --- Add Metric ---
    elements.append(Paragraph(f"Number of people who required intubation: {count_intubation}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # --- Add DataFrame as Table ---
    # Convert df to list of lists for ReportLab Table
    data = [df.columns.to_list()] + df.values.tolist()
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
    ]))
    elements.append(table)

    # --- Build PDF ---
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer

# -----------------------
# Streamlit download button
# -----------------------
if st.button("Download Counts as PDF"):
    pdf_buffer = export_counts_to_pdf()
    st.download_button(
        label="Download PDF",
        data=pdf_buffer,
        file_name="covid_counts.pdf",
        mime="application/pdf"
    )