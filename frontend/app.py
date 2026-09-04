
"""
PrescriptionLens AI - Streamlit Frontend
Prescription Image -> OpenCV -> OCR -> AI Chatbot
-> Medicine Info + Timing Checklist
"""

import base64
import os

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
)


st.set_page_config(
    page_title="PrescriptionLens AI",
    page_icon="💊",
    layout="wide",
)


# ---------- Session State ----------

if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

if "verified_text" not in st.session_state:
    st.session_state.verified_text = ""

if "medicines" not in st.session_state:
    st.session_state.medicines = []

if "checklist_state" not in st.session_state:
    st.session_state.checklist_state = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "ocr_done" not in st.session_state:
    st.session_state.ocr_done = False

if "processed_image_bytes" not in st.session_state:
    st.session_state.processed_image_bytes = None

if "original_image_bytes" not in st.session_state:
    st.session_state.original_image_bytes = None


# ---------- Disclaimer ----------

DISCLAIMER = (
    "**Disclaimer:** This application extracts and organizes information "
    "from a prescription and provides general educational information. "
    "It does not diagnose conditions or prescribe/change medication. "
    "Always verify medication instructions with your doctor or pharmacist."
)


# ---------- Timing Helper ----------

def parse_timing_to_slots(timing_text: str):

    if not timing_text:
        return []

    timing_lower = timing_text.lower()

    slots = []

    mapping = {
        "morning": "Morning",
        "breakfast": "Morning",
        "afternoon": "Afternoon",
        "noon": "Afternoon",
        "lunch": "Afternoon",
        "evening": "Evening",
        "night": "Night",
        "dinner": "Night",
        "bedtime": "Night",
    }

    for keyword, slot in mapping.items():

        if keyword in timing_lower and slot not in slots:

            slots.append(slot)

    return slots


# ---------- Sidebar ----------

st.sidebar.title("💊 PrescriptionLens AI")


section = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Home",
        "📷 Upload Prescription",
        "🔍 OCR Results",
        "💊 Medicine Information",
        "⏰ Timing Checklist",
        "🤖 AI Chatbot",
        "💡 General Care Tips",
    ],
)


st.sidebar.markdown("---")

st.sidebar.caption(DISCLAIMER)


# ============================================================
# HOME
# ============================================================

if section == "🏠 Home":

    st.title("💊 PrescriptionLens AI")

    st.subheader(
        "OCR Prescription Organizer & Educational Chatbot"
    )

    st.write(
        """
        PrescriptionLens AI helps you digitize and organize a prescription:

        1. **Upload** a photo of your prescription.
        2. **OpenCV** preprocesses the image for better OCR accuracy.
        3. **EasyOCR** extracts the text.
        4. You can review and correct the OCR text.
        5. An **LLM** extracts structured medicine details.
        6. Get a **timing checklist**.
        7. Ask the **AI chatbot** questions about your prescription.
        8. View general **wellness tips**.
        """
    )

    st.info(DISCLAIMER)

    st.markdown(
        "Use the sidebar to get started with "
        "**📷 Upload Prescription**."
    )


# ============================================================
# UPLOAD PRESCRIPTION
# ============================================================

elif section == "📷 Upload Prescription":

    st.title("📷 Upload Prescription")

    uploaded_file = st.file_uploader(
        "Upload a prescription image (JPG, PNG)",
        type=["jpg", "jpeg", "png"]
    )


    if uploaded_file is not None:

        image_bytes = uploaded_file.read()

        st.session_state.original_image_bytes = image_bytes


        # Streamlit compatibility fix
        st.image(
            image_bytes,
            caption="Uploaded Prescription",
            use_column_width=True
        )


        if st.button(
            "Run OCR",
            type="primary"
        ):

            with st.spinner(
                "Processing image and extracting text..."
            ):

                try:

                    # Convert image to Base64
                    b64_image = base64.b64encode(
                        image_bytes
                    ).decode("utf-8")


                    # IMPORTANT:
                    # Send image in JSON body instead of URL parameters
                    response = requests.post(
                        f"{BACKEND_URL}/ocr",
                        json={
                            "image_base64": b64_image
                        },
                        timeout=120,
                    )


                    if response.status_code == 200:

                        result = response.json()


                        if result["success"]:

                            st.session_state.extracted_text = (
                                result["extracted_text"]
                            )

                            st.session_state.verified_text = (
                                result["extracted_text"]
                            )

                            st.session_state.ocr_done = True


                            st.success(
                                "OCR completed! "
                                "Go to '🔍 OCR Results' to review."
                            )


                        else:

                            st.session_state.ocr_done = False

                            st.error(
                                result.get(
                                    "message",
                                    "OCR failed to extract text."
                                )
                            )


                    else:

                        st.error(
                            f"Backend error: "
                            f"{response.status_code} - "
                            f"{response.text}"
                        )


                except requests.exceptions.ConnectionError:

                    st.error(
                        f"Could not connect to backend at "
                        f"{BACKEND_URL}. "
                        "Make sure the FastAPI server is running."
                    )


                except Exception as e:

                    st.error(
                        f"Unexpected error: {str(e)}"
                    )


    else:

        st.info(
            "Please upload a prescription image to begin."
        )


# ============================================================
# OCR RESULTS
# ============================================================

elif section == "🔍 OCR Results":

    st.title("🔍 OCR Results")


    if st.session_state.original_image_bytes is None:

        st.warning(
            "Please upload a prescription image first "
            "(see '📷 Upload Prescription')."
        )


    else:

        col1, col2 = st.columns(2)


        with col1:

            st.subheader("Original Image")

            st.image(
                st.session_state.original_image_bytes,
                use_column_width=True
            )


        with col2:

            st.subheader("Extracted Text")


            if st.session_state.ocr_done:

                st.text_area(
                    "Raw OCR output (for reference)",
                    value=st.session_state.extracted_text,
                    height=200,
                    disabled=True,
                )


            else:

                st.error(
                    "OCR did not extract any text. "
                    "Please try a clearer image below."
                )


        st.markdown("---")


        st.subheader("✏️ Review & Correct Text")


        st.write(
            "OCR is not always perfect. Please review and correct "
            "the text below before sending it for medicine extraction."
        )


        st.session_state.verified_text = st.text_area(
            "Verified Prescription Text",
            value=st.session_state.verified_text,
            height=250,
        )


        if st.button(
            "Confirm & Extract Medicines",
            type="primary"
        ):


            if not st.session_state.verified_text.strip():

                st.warning(
                    "Please provide some prescription text "
                    "before extracting medicines."
                )


            else:

                with st.spinner(
                    "Extracting structured medicine information..."
                ):

                    try:

                        response = requests.post(
                            f"{BACKEND_URL}/analyze",
                            json={
                                "prescription_text":
                                    st.session_state.verified_text
                            },
                            timeout=60,
                        )


                        if response.status_code == 200:

                            result = response.json()

                            st.session_state.medicines = (
                                result["medicines"]
                            )


                            st.success(
                                f"Extracted "
                                f"{len(result['medicines'])} medicine(s). "
                                "Go to '💊 Medicine Information' "
                                "to view."
                            )


                        else:

                            st.error(
                                f"Backend error: "
                                f"{response.status_code} - "
                                f"{response.text}"
                            )


                    except requests.exceptions.ConnectionError:

                        st.error(
                            f"Could not connect to backend "
                            f"at {BACKEND_URL}."
                        )


                    except Exception as e:

                        st.error(
                            f"Unexpected error: {str(e)}"
                        )


# ============================================================
# MEDICINE INFORMATION
# ============================================================

elif section == "💊 Medicine Information":

    st.title("💊 Medicine Information")


    if not st.session_state.medicines:

        st.warning(
            "No medicine data yet. Please complete OCR "
            "and extraction in '🔍 OCR Results' first."
        )


    else:

        for idx, med in enumerate(
            st.session_state.medicines
        ):

            name = med.get(
                "name"
            ) or "Unnamed medicine"


            with st.container(border=True):

                st.markdown(
                    f"### 💊 {name}"
                )


                c1, c2, c3 = st.columns(3)


                c1.markdown(
                    f"**Strength:** "
                    f"{med.get('strength') or '—'}"
                )


                c1.markdown(
                    f"**Dosage:** "
                    f"{med.get('dosage') or '—'}"
                )


                c2.markdown(
                    f"**Frequency:** "
                    f"{med.get('frequency') or '—'}"
                )


                c2.markdown(
                    f"**Timing:** "
                    f"{med.get('timing') or '—'}"
                )


                c3.markdown(
                    f"**Food relation:** "
                    f"{med.get('food_relation') or '—'}"
                )


                c3.markdown(
                    f"**Duration:** "
                    f"{med.get('duration') or '—'}"
                )


        st.caption(
            "Fields shown as '—' were not explicitly mentioned "
            "in the prescription and have not been guessed."
        )


# ============================================================
# TIMING CHECKLIST
# ============================================================

elif section == "⏰ Timing Checklist":

    st.title("⏰ Timing Checklist")


    if not st.session_state.medicines:

        st.warning(
            "No medicine data yet. "
            "Please complete extraction first."
        )


    else:

        st.write(
            "Check off each dose as you take it. "
            "This checklist reflects only the timing "
            "explicitly written in the prescription."
        )


        for idx, med in enumerate(
            st.session_state.medicines
        ):

            name = med.get(
                "name"
            ) or f"Medicine {idx + 1}"


            timing_text = med.get(
                "timing"
            ) or ""


            food_relation = med.get(
                "food_relation"
            ) or ""


            slots = parse_timing_to_slots(
                f"{timing_text} {food_relation}"
            )


            st.markdown(
                f"#### {name}"
            )


            if not slots:

                st.caption(
                    "No explicit timing was found in the "
                    "prescription for this medicine. "
                    "No schedule has been assumed."
                )

                continue


            for slot in slots:

                key = f"check_{idx}_{slot}"


                if key not in st.session_state.checklist_state:

                    st.session_state.checklist_state[key] = False


                label = slot


                if (
                    slot == "Morning"
                    and "breakfast"
                    in food_relation.lower()
                ):

                    label = "Morning — After breakfast"


                elif (
                    slot == "Night"
                    and "dinner"
                    in food_relation.lower()
                ):

                    label = "Night — After dinner"


                elif food_relation:

                    label = (
                        f"{slot} — "
                        f"{food_relation}"
                    )


                st.session_state.checklist_state[key] = (
                    st.checkbox(
                        label,
                        value=st.session_state.checklist_state[key],
                        key=key
                    )
                )


            st.markdown("---")


# ============================================================
# AI CHATBOT
# ============================================================

elif section == "🤖 AI Chatbot":

    st.title("🤖 AI Chatbot")


    if not st.session_state.verified_text:

        st.warning(
            "Please complete OCR first so the chatbot "
            "has prescription context."
        )


    else:

        st.caption(
            "Ask about your prescription. General medical info "
            "will be labeled as educational only — "
            "this is not a diagnosis."
        )


        for role, message in st.session_state.chat_history:

            with st.chat_message(role):

                st.write(message)


        user_question = st.chat_input(
            "Ask a question about your prescription..."
        )


        if user_question:

            st.session_state.chat_history.append(
                ("user", user_question)
            )


            with st.chat_message("user"):

                st.write(user_question)


            with st.chat_message("assistant"):

                with st.spinner("Thinking..."):

                    try:

                        response = requests.post(
                            f"{BACKEND_URL}/chat",
                            json={
                                "question":
                                    user_question,

                                "prescription_text":
                                    st.session_state.verified_text,

                                "medicines":
                                    st.session_state.medicines,
                            },
                            timeout=60,
                        )


                        if response.status_code == 200:

                            answer = response.json()["answer"]


                        else:

                            answer = (
                                f"Backend error: "
                                f"{response.status_code} - "
                                f"{response.text}"
                            )


                    except requests.exceptions.ConnectionError:

                        answer = (
                            f"Could not connect to backend "
                            f"at {BACKEND_URL}."
                        )


                    except Exception as e:

                        answer = (
                            f"Unexpected error: {str(e)}"
                        )


                    st.write(answer)


                    st.session_state.chat_history.append(
                        ("assistant", answer)
                    )


# ============================================================
# GENERAL CARE TIPS
# ============================================================

elif section == "💡 General Care Tips":

    st.title(
        "💡 General Care & Wellness Tips"
    )


    st.write(
        """
        These are general, educational suggestions only — not medical advice:

        - 💧 Stay hydrated throughout the day.
        - 🛏️ Get adequate rest to support recovery.
        - ⏰ Take medicines as instructed on the prescription, at the times noted.
        - ✅ Use the timing checklist to help avoid missed or duplicate doses.
        - 📞 Contact your doctor or pharmacist if any instruction is unclear.
        - 🚫 Never stop, change, or combine medications without professional advice.
        """
    )


    st.warning(DISCLAIMER)
