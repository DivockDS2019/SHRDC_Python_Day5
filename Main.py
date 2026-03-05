import streamlit as st
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from datetime import datetime
import os



# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Covid-19 Dashboard", layout="wide")
st.title("Covid-19 (Data Visualisation + PDF Export)")

df = pd.read_csv('dataset.csv')
dictionary = pd.read_excel('data_dictionary.xlsx')



#--------------------------------------------------
# CREATING MULTIPLE PAGES 
#-------------------------------------------------
st.sidebar.header("Pages")

