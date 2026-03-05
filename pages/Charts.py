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
from PIL import Image as PILImage
import os


st.set_page_config(page_title="Charts", layout="wide")
st.title("Covid-19 Data Charts")

df = pd.read_csv('dataset.csv')
dictionary = pd.read_excel('data_dictionary.xlsx')

# MAPPING 

df["SEX"] = df["SEX"].map({1:"FEMALE", 2:"MALE", 99:"UNKNOWN"})
df["OUTCOME"] = df["OUTCOME"].map({1:"POSITIVE", 2:"NEGAi wTIVE", 3:"PENDING"})
df["COUNTRY OF ORIGIN"] = df["NATIONALITY"].map({1:"MEXICAN", 2:"FOREIGN", 99:"UNKNOWN"})
yn_map = {1:"YES", 2:"NO", 97:"DOES NOT APPLY", 98:"IGNORED", 99:"UNKNOWN"}

cols = [
"INTUBATED","PNEUMONIA","PREGNANCY", "SPEAKS_NATIVE_LANGUAGE","DIABETES","COPD","ASTHMA","INMUSUPR",
"HYPERTENSION","OTHER_DISEASE","CARDIOVASCULAR","OBESITY", "CHRONIC_KIDNEY","TOBACCO","ANOTHER CASE", "ICU", "MIGRANT"
]

for c in cols:
    df[c] = df[c].map(yn_map)

print(df)

#--------------------------
# Button 1: Drop down 
#--------------------------
chart_choice = st.selectbox(
    "Select Chart to Display and Download",
    ["COVID-19 Cases by Age Group", "ICU-Disease Correlation", "Deceased Data"]
) #------------- edit later 

if chart_choice == "COVID-19 Cases by Age Group":

    # Add slider for age group bin size
    bin_size = st.slider("Select Age Group Bin Size", min_value=5, max_value=50, value=10, step=5)


    max_age = df["AGE"].max()
    bins = list(range(0, int(max_age) + bin_size, bin_size))
    labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)]

    df["AGE_GROUP"] = pd.cut(df["AGE"], bins=bins, labels=labels)

    tab1, tab2 = st.tabs(["Sorted by Age Group", "Sorted by Age Group and Gender"])

    with tab1:
    #Q1
        age_counts = df["AGE_GROUP"].value_counts().sort_index()
        st.title("Distribution of Cases by Age Group")
        st.bar_chart(age_counts)


    with tab2:
        #Q2
        gender_age_dist = df.groupby(["AGE_GROUP","SEX"]).size().unstack()
        st.title("Distribution of Cases by Gender & Age Group")
        st.bar_chart(gender_age_dist)

elif chart_choice == "ICU-Disease Correlation":
    disease_cols = ["DIABETES", "COPD", "ASTHMA", "INMUSUPR", "HYPERTENSION", "CARDIOVASCULAR", "OBESITY", "CHRONIC_KIDNEY", "TOBACCO"]
    # Convert Yes/No to numeric
    for col in disease_cols + ["ICU"]:
        df[col] = df[col].map({"YES": 1, "NO": 0})

# Calculate counts for each disease
    counts = []
    for disease in disease_cols:
        total = df[disease].sum()
        icu = df[(df[disease]==1) & (df["ICU"]==1)].shape[0]
        counts.append({"Disease": disease, "Type": "Total", "Count": total})
        counts.append({"Disease": disease, "Type": "ICU", "Count": icu})

    counts_df = pd.DataFrame(counts)
    
    fig = px.bar(
    counts_df,
    y="Disease",
    x="Count",
    color="Type",
    barmode="group",  # <-- ensures side-by-side bars
    orientation="h",
    title="Patients with Disease vs ICU Admissions"
    )

    st.plotly_chart(fig, use_container_width=True)


else:
    st.subheader("Pie Chart: Disease-Deceased Distribution")
    disease_cols = ["DIABETES", "COPD", "ASTHMA", "INMUSUPR",
                "HYPERTENSION", "CARDIOVASCULAR", "OBESITY",
                "CHRONIC_KIDNEY", "TOBACCO"]
    
    deceased_patients = df[df["DATE_OF_DEATH"].notnull()]

    print(deceased_patients.head())
    print("Number of deceased patients:", len(deceased_patients))

    counts = {disease: deceased_patients[disease].eq("YES").sum() for disease in disease_cols}
    pie_data = pd.DataFrame({
        "Disease": list(counts.keys()),
        "Count": list(counts.values())
    })

    pie_data = pie_data[pie_data["Count"] > 0]

    st.vega_lite_chart(
        pie_data,
        {
            "mark": "arc",
            "encoding": {
                "theta": {"field": "Count", "type": "quantitative"},
                "color": {"field": "Disease", "type": "nominal"},
            },
        },
        use_container_width=True,
    )

# --- PDF generation function ---
def export_chart_to_pdf(chart_choice, chart_img_buffer):
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # --- Add Logo ---
    logo_path = "shrdc_logo.png"
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=150, height=50))
        elements.append(Spacer(1, 20))

    # --- Add Chart Title ---
    elements.append(Paragraph(chart_choice, styles["Heading1"]))
    elements.append(Spacer(1, 10))

    # --- Add Timestamp ---
    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 20))

    # --- Add Chart Image ---
    chart_img_buffer.seek(0)
    elements.append(Image(chart_img_buffer, width=450, height=250))

    # --- Build PDF ---
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer


# -------------------
# Create chart image from chart_choice
# -------------------
chart_img_buffer = io.BytesIO()

if chart_choice == "COVID-19 Cases by Age Group":
    fig, ax = plt.subplots(figsize=(8,4))
    age_counts.plot(kind="bar", ax=ax)
    ax.set_title("COVID-19 Cases by Age Group")
    ax.set_xlabel("Age Group")
    ax.set_ylabel("Number of Cases")
    plt.tight_layout()
    plt.savefig(chart_img_buffer, format="png")
    plt.close(fig)

elif chart_choice == "ICU-Disease Correlation":
    # For Plotly chart
    fig.write_image(chart_img_buffer, format="png")

else:  # Deceased Pie Chart
    fig, ax = plt.subplots(figsize=(6,6))
    ax.pie(pie_data["Count"], labels=pie_data["Disease"], autopct='%1.1f%%', startangle=90)
    ax.set_title("Diseases among Deceased Patients")
    plt.tight_layout()
    plt.savefig(chart_img_buffer, format="png")
    plt.close(fig)

chart_img_buffer.seek(0)

# -------------------
# Streamlit download button
# -------------------
if st.button("Download Current Chart as PDF"):
    pdf_buffer = export_chart_to_pdf(chart_choice, chart_img_buffer)
    st.download_button(
        label="Download PDF",
        data=pdf_buffer,
        file_name=f"{chart_choice}.pdf",
        mime="application/pdf"
    )