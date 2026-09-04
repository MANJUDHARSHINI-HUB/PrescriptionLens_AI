"""
PrescriptionLens AI - FastAPI Backend
Endpoints: /health, /ocr, /analyze, /chat
"""

import base64
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.ocr_service import process_prescription_image
from backend.extraction_service import extract_medicines, MedicineInfo
from backend.chat_service import answer_question


app = FastAPI(
    title="PrescriptionLens AI API",
    description="OCR + LLM powered prescription organizer backend",
    version="1.0.0",
)


# ---------- CORS ----------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Request / Response Models ----------

class OCRRequest(BaseModel):
    image_base64: str


class OCRResponse(BaseModel):
    success: bool
    extracted_text: str
    message: Optional[str] = None


class AnalyzeRequest(BaseModel):
    prescription_text: str


class AnalyzeResponse(BaseModel):
    success: bool
    medicines: List[MedicineInfo]
    message: Optional[str] = None


class ChatRequest(BaseModel):
    question: str
    prescription_text: str
    medicines: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    success: bool
    answer: str


# ---------- Health ----------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "PrescriptionLens AI API"
    }


# ---------- OCR ----------

@app.post("/ocr", response_model=OCRResponse)
async def ocr_endpoint(request: OCRRequest):

    image_base64 = request.image_base64

    if not image_base64:
        raise HTTPException(
            status_code=400,
            detail="No image data provided"
        )

    try:
        image_bytes = base64.b64decode(image_base64)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid base64 image data"
        )

    try:
        extracted_text, processed_ok = process_prescription_image(
            image_bytes
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}"
        )

    if not processed_ok or not extracted_text.strip():

        return OCRResponse(
            success=False,
            extracted_text="",
            message=(
                "OCR could not extract readable text from this image. "
                "Please upload a clearer prescription image or type "
                "the text manually."
            ),
        )

    return OCRResponse(
        success=True,
        extracted_text=extracted_text
    )


# ---------- Medicine Analysis ----------

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_endpoint(request: AnalyzeRequest):

    if (
        not request.prescription_text
        or not request.prescription_text.strip()
    ):
        raise HTTPException(
            status_code=400,
            detail="prescription_text cannot be empty"
        )

    try:

        medicines = extract_medicines(
            request.prescription_text
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )

    return AnalyzeResponse(
        success=True,
        medicines=medicines
    )


# ---------- Chat ----------

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):

    if (
        not request.question
        or not request.question.strip()
    ):
        raise HTTPException(
            status_code=400,
            detail="question cannot be empty"
        )

    if (
        not request.prescription_text
        or not request.prescription_text.strip()
    ):
        raise HTTPException(
            status_code=400,
            detail="prescription_text cannot be empty"
        )

    try:

        answer = answer_question(
            question=request.question,
            prescription_text=request.prescription_text,
            medicines=request.medicines or [],
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )

    return ChatResponse(
        success=True,
        answer=answer
    )

