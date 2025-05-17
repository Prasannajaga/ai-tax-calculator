import streamlit as st
from PIL import Image
import io
import time
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Tax assistant",
    page_icon="🖼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a more beautiful UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #475569;
        margin-bottom: 2rem;
        text-align: center;
    }
    .card {
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: #F8FAFC;
    }
    .generated-text {
        background-color: #F1F5F9;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
        margin-top: 1rem;
    }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
    }
    .upload-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 2px dashed #CBD5E1;
        border-radius: 10px;
        padding: 2rem;
        margin-bottom: 1rem;
        background-color: #F8FAFC;
    }
    .success-message {
        color: #047857;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    .loading-spinner {
        text-align: center;
        margin: 2rem 0;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        font-size: 0.8rem;
        color: #64748B;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>Tax assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Upload an image and let AI Save your tax</p>", unsafe_allow_html=True)

# Function to generate text from image


# Load Gemini API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set.")

genai.configure(api_key=GEMINI_API_KEY)



def generate_text_from_image(image):
    # Convert PIL image to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    img_data = img_bytes.read()

    # Prepare Gemini model and system/user prompts
    model = genai.GenerativeModel("gemini-2.0-flash")

    system_prompt = (
        "You are a financial assistant. The user will provide salary-related components.\n"
        "Based on this, calculate the estimated annual income tax under the New Tax Regime (FY 2024-25) in India.\n"
        "Include 4% health and education cess in the final tax and show step-by-step calculations.\n\n"

        "👉 Ask the user to input the following:\n"
        "- Gross Salary (₹) [required]\n"
        "- Incentive (₹) [optional, default 0]\n"
        "- Joining Bonus (₹) [optional, default 0]\n"
        "- Stock Grant / RSU (₹) [optional, default 0]\n"
        "- Are joining bonus and stock taxable this year? [Yes / No]\n\n"

        "📌 Validate all numeric inputs. If any required field is missing or invalid, prompt the user to enter it again.\n\n"

        "🧾 Perform two tax calculations:\n"
        "1. Case A: Taxable Income = Gross Salary + Incentive\n"
        "2. Case B: Taxable Income = Gross Salary + Incentive + (Joining Bonus + Stock), only if taxable this year\n\n"

        "📊 Use the following tax slabs under the New Tax Regime FY 2024-25:\n"
        "- ₹0 – ₹3,00,000           : 0%\n"
        "- ₹3,00,001 – ₹6,00,000    : 5%\n"
        "- ₹6,00,001 – ₹9,00,000    : 10%\n"
        "- ₹9,00,001 – ₹12,00,000   : 15%\n"
        "- ₹12,00,001 – ₹15,00,000  : 20%\n"
        "- ₹15,00,001 and above     : 30%\n\n"

        "✅ For both Case A and Case B, provide output in the following table format:\n\n"

        "**Case X:**\n"
        "| Description             | Amount (₹) |\n"
        "|-------------------------|------------|\n"
        "| Taxable Income          | x,xx,xxx   |\n"
        "| Tax on 0–3L @ 0%        | x,xxx      |\n"
        "| Tax on 3L–6L @ 5%       | x,xxx      |\n"
        "| Tax on 6L–9L @ 10%      | x,xxx      |\n"
        "| Tax on 9L–12L @ 15%     | x,xxx      |\n"
        "| Tax on 12L–15L @ 20%    | x,xxx      |\n"
        "| Tax on 15L+ @ 30%       | x,xxx      |\n"
        "| Total Tax (before Cess) | xx,xxx     |\n"
        "| 4% Health & Edu Cess    | x,xxx      |\n"
        "| Monthly inhand          | x,xxx      |\n"
        "| **Final Tax Payable**   | **xx,xxx** |\n\n"

        "Repeat the table for both Case A and Case B with appropriate values. Ensure outputs are clear and formatted in rows and columns for readability."
    )


    user_prompt = (
        "Analyze this salary slip or tax document image and calculate the in-hand and monthly salary. "
        "Provide a detailed breakdown of deductions, taxes, and net salary. "
        "If the image is not a salary slip, say so. Then calculate estimated tax as per instructions."
    )   

    # Correct way to send an image with prompt to Gemini
    response = model.generate_content(
        [
            {"role": "user", "parts": [
                {"text": system_prompt + "\n" + user_prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_data
                    }
                }
            ]}
        ]
    )


    # Send image and prompt to Gemini
    # response = model.generate_content(
    #     [system_prompt,
    #      user_prompt,
    #      genai.types.Blob(mime_type="image/jpg", data=img_data)]
    # )

    # Extract and return the text response
    return response.text.strip() if hasattr(response, "text") else str(response)

   

# Main app layout
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    
    # File uploader
    st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Uploaded Image", use_container_width =True)
            st.markdown("<p class='success-message'>✅ Image uploaded successfully!</p>", unsafe_allow_html=True)
        
        # Generate button
        if st.button("Generate Insights"):
            with st.spinner("Analyzing image..."):
                # In a real app, you would convert the image to base64 and send to API
                # image_bytes = io.BytesIO()
                # image.save(image_bytes, format='JPEG')
                # image_b64 = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
                
                # Generate text
                generated_text = generate_text_from_image(image)
                
                # Display generated text with nice formatting
                st.markdown("<div class='generated-text'>", unsafe_allow_html=True)
                st.markdown("### Image Analysis Results")
                st.write(generated_text)
                st.markdown("</div>", unsafe_allow_html=True)

                # Enable chat after generating text
                st.markdown("### Continue the Conversation")
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = [
                        {"role": "assistant", "content": generated_text}
                    ]

                user_input = st.text_input("Ask a follow-up question or provide more info:", key="chat_input")
                if st.button("Send", key="send_btn") and user_input.strip():
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    with st.spinner("AI is replying..."):
                        # Prepare chat history for Gemini
                        chat_parts = []
                        for msg in st.session_state.chat_history:
                            chat_parts.append({"role": msg["role"], "parts": [{"text": msg["content"]}]})
                        # Use the same model as before
                        model = genai.GenerativeModel("gemini-2.0-flash")
                        response = model.generate_content(chat_parts)
                        reply = response.text.strip() if hasattr(response, "text") else str(response)
                        st.session_state.chat_history.append({"role": "assistant", "content": reply})

                # Display chat history
                for msg in st.session_state.chat_history[1:]:
                    if msg["role"] == "user":
                        st.markdown(f"**You:** {msg['content']}")
                    else:
                        st.markdown(f"**AI:** {msg['content']}")


    
    st.markdown("</div>", unsafe_allow_html=True)

# App instructions
with st.expander("How to use this app"):
    st.markdown("""
    1. *Upload an image* using the file uploader above
    2. Click the *Generate Insights* button
    3. The AI will analyze your image and provide detailed text descriptions
    
    This app uses advanced AI vision models to generate informative and creative descriptions of your images.
    """)

# Settings in sidebar
with st.sidebar:
    st.header("Settings")
    st.slider("Detail Level", 1, 5, 3)
    st.selectbox("Analysis Style", ["Descriptive", "Creative", "Technical", "Emotional"])
    st.checkbox("Include metadata analysis")

# Footer
st.markdown("<div class='footer'>© 2025 Image Insight Generator • Built with Streamlit and AI</div>", unsafe_allow_html=True)