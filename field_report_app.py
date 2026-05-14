import streamlit as st
from streamlit_gps_location import gps_location_button
from fpdf import FPDF
from PIL import Image
from datetime import datetime
import tempfile
import os

st.set_page_config(page_title="Field Scientist Report App",layout="centered")

st.title("Field Scientist Report App")
st.header("1. Researcher Information")

researcher_name = st.text_input("Researcher name")
discovery_title = st.text_input("Title of discovery")
notes = st.text_area("Description / notes")

st.header("2. GPS Location")

location_data = gps_location_button(buttonText="Get my location",key="gps")

latitude = None
longitude = None

if location_data:
    latitude = location_data.get("latitude")
    longitude = location_data.get("longitude")

    st.write("Location data:")
    st.json(location_data)

    if latitude is not None and longitude is not None:
        st.success("Location captured successfully!")
        st.map({"lat": [latitude],"lon": [longitude]})
    else:
        st.warning("Location not captured yet. Please allow location access.")
else:
    st.info("Click the button to capture your location.")

st.header("3. Visual Evidence")
photo = st.camera_input("Take a photo as evidence")

if photo is not None:
    st.image(photo, caption="Evidence photo", use_container_width=True)

st.header("4. Generate PDF Report")

def create_pdf(name, title, description, lat, lon, photo_file):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_fill_color(46, 125, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 18, "FIELD REPORT", ln=True, align="C", fill=True)

    pdf.ln(10)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 8, f"Researcher: {name}", ln=False)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%d/%m/%Y')}", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Coordinates: Lat {lat}, Lon {lon}", ln=True)

    pdf.ln(6)

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, f"Finding: {title}", ln=True)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Observations:", ln=True)

    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, description)

    if photo_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
            image = Image.open(photo_file)
            image = image.convert("RGB")
            image.save(tmp_img.name)

            pdf.ln(5)
            pdf.image(tmp_img.name, x=40, w=120)

            os.remove(tmp_img.name)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf.output(tmp_pdf.name)
        return tmp_pdf.name


if st.button("Generate PDF Report"):
    if not researcher_name:
        st.error("Please enter the researcher name.")
    elif not discovery_title:
        st.error("Please enter the title of the discovery.")
    elif not notes:
        st.error("Please enter the description or notes.")
    elif latitude is None or longitude is None:
        st.error("Please capture your GPS location.")
    elif photo is None:
        st.error("Please take a photo as evidence.")
    else:
        pdf_path = create_pdf(researcher_name, discovery_title, notes, latitude, longitude, photo)

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Download PDF Report",
                data=pdf_file,
                file_name="field_report.pdf",
                mime="application/pdf"
            )
        st.success("PDF report generated successfully!")