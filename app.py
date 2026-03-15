import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt

# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(page_title="Women Safety Analytics", layout="wide")

st.markdown("""
<style>
.stApp{
background: linear-gradient(to right,#ffc0cb,#e6ccff);
}
h1{
text-align:center;
color:#8B008B;
}
</style>
""", unsafe_allow_html=True)

st.title("🚺 Women Safety Analytics Dashboard")

# -------------------------
# GOOGLE SHEETS CONNECTION
# -------------------------

scope = [
"https://spreadsheets.google.com/feeds",
"https://www.googleapis.com/auth/drive"
]

# -------------------------
# GOOGLE SHEETS CONNECTION
# -------------------------

import json

scope = [
"https://spreadsheets.google.com/feeds",
"https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(st.secrets["gcp_service_account"])

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict,
    scope
)

client = gspread.authorize(creds)

sheet = client.open("Women Safety Data").sheet1)

client = gspread.authorize(creds)

sheet = client.open("Women Safety Data").sheet1

data = sheet.get_all_records()

df = pd.DataFrame(data)

# -------------------------
# CLEAN DATA
# -------------------------

df.columns = df.columns.str.strip()

df = df[df["lat"] != ""]
df = df[df["lon"] != ""]

df["lat"] = df["lat"].astype(float)
df["lon"] = df["lon"].astype(float)

# Fix spacing and capitalization
df["danger_level"] = df["danger_level"].astype(str).str.strip().str.capitalize()

# -------------------------
# INCIDENT REPORT FORM
# -------------------------

st.header("📍 Report Incident")

with st.form("incident_form"):

    location = st.text_input("Location")

    incident = st.text_input("Incident")

    time = st.text_input("Time")

    description = st.text_area("Description")

    lat = st.text_input("Latitude")

    lon = st.text_input("Longitude")

    danger_level = st.selectbox(
        "Danger Level",
        ["Safe", "Warning", "Danger"]
    )

    submit = st.form_submit_button("Submit")

    if submit:

        sheet.append_row([
            location,
            incident,
            time,
            description,
            lat,
            lon,
            danger_level
        ])

        st.success("Incident Added Successfully")

# -------------------------
# SAFETY MAP
# -------------------------

st.header("🗺 Women Safety Map")

m = folium.Map(location=[12.9716,77.5946], zoom_start=12)

# Map markers
for index,row in df.iterrows():

    level = row["danger_level"]

    if level == "Danger":
        color = "red"

    elif level == "Warning":
        color = "orange"

    else:
        color = "green"

    popup = f"""
    <b>Location:</b> {row['Location']}<br>
    <b>Incident:</b> {row['Incident']}<br>
    <b>Time:</b> {row['Time']}<br>
    <b>Description:</b> {row['Description']}
    """

    folium.Marker(
        location=[row["lat"],row["lon"]],
        popup=popup,
        icon=folium.Icon(color=color)
    ).add_to(m)

# -------------------------
# HEATMAP (Danger Zones)
# -------------------------

danger_data = df[df["danger_level"]=="Danger"][["lat","lon"]]

if not danger_data.empty:
    HeatMap(danger_data.values, radius=25).add_to(m)

st_folium(m,width=1000,height=500)

# -------------------------
# ANALYTICS DASHBOARD
# -------------------------

st.header("📊 Safety Analytics")

if not df.empty:

    # Incident distribution
    st.subheader("🚨 Incident Distribution")

    incident_counts = df["Incident"].value_counts()

    fig1, ax1 = plt.subplots()

    ax1.pie(
        incident_counts,
        labels=incident_counts.index,
        autopct="%1.1f%%",
        startangle=90
    )

    ax1.axis("equal")

    st.pyplot(fig1)

    # Safety levels graph
    st.subheader("🚦 Area Safety Levels")

    danger_counts = df["danger_level"].value_counts()

    color_map = {
        "Safe": "green",
        "Warning": "lightsalmon",
        "Danger": "red"
    }

    colors = [color_map[level] for level in danger_counts.index]

    fig2, ax2 = plt.subplots()

    ax2.bar(
        danger_counts.index,
        danger_counts.values,
        color=colors
    )

    ax2.set_ylabel("Number of Incidents")

    ax2.set_xlabel("Safety Level")

    st.pyplot(fig2)

else:

    st.write("No data available yet.")
