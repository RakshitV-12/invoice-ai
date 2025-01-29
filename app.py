from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import pandas as pd
import google.generativeai as genai
import io

# Load environment variables
load_dotenv()

# Configure Google API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)  # Initialize with your Google API key

# Function to process images
def input_image_setup(uploaded_file):
    if uploaded_file:
        bytes_data = uploaded_file.getvalue()
        return [{"mime_type": uploaded_file.type, "data": bytes_data}]
    else:
        return None

# Function to get Gemini response
def get_gemini_response(input_prompt, image_parts, user_query):
    # Initialize the model with the correct name (Gemini model in your case)
    model = genai.GenerativeModel('gemini-1.5-flash')  # Use the correct model name

    # Generate content using the model with provided inputs
    response = model.generate_content([input_prompt, image_parts[0], user_query]) 
    return response.text  # Assuming response.text is where the content is stored

# Function to convert response to Excel format
def response_to_excel(response_text):
    # Converting response into structured format
    data = {"Response": [response_text]}  # Simple single-column DataFrame
    df = pd.DataFrame(data)

    # Save DataFrame to an in-memory Excel file
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Invoice Analysis")
    
    return excel_buffer

# Streamlit UI
st.set_page_config(page_title="Gemini Invoice Analyzer")
st.header("Gemini Invoice Analysis")

# User Input & File Upload
user_query = st.text_input("Enter your question:", key="input")
uploaded_file = st.file_uploader("Upload an invoice image (JPG, PNG):", type=["jpg", "jpeg", "png"])

# Display uploaded image
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

# Prompt Definition
input_prompt = "You are an expert in understanding invoices. You will receive invoice images and answer questions based on the input image."

# Submit Button
if st.button("Analyze Invoice"):
    if uploaded_file is None:
        st.error("⚠️ Please upload an invoice image before submitting.")
    else:
        image_data = input_image_setup(uploaded_file)  # Prepare image data for the model
        response = get_gemini_response(input_prompt, image_data, user_query)  # Get the model's response

        # Convert response to Excel
        excel_data = response_to_excel(response)

        # Provide a download button for the user
        st.subheader("Download Response as Excel:")
        st.download_button(label="📥 Download Excel File", data=excel_data, file_name="invoice_analysis.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
