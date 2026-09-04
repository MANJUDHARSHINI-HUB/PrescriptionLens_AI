"""
OCR Service
Uses OpenCV for preprocessing and EasyOCR for text extraction.
"""
import io
from typing import Tuple

import cv2
import numpy as np
from PIL import Image

_reader = None


def _get_reader():
    """Lazy-load EasyOCR reader (heavy import, only load once)."""
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def bytes_to_cv2_image(image_bytes: bytes) -> np.ndarray:
    """Convert raw image bytes to an OpenCV BGR image."""
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    np_image = np.array(pil_image)
    cv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
    return cv_image


def preprocess_image(cv_image: np.ndarray) -> np.ndarray:
    """
    Basic OpenCV preprocessing pipeline to improve OCR accuracy:
    - resize (upscale small images)
    - grayscale
    - denoising
    - adaptive thresholding for contrast improvement
    """
    height, width = cv_image.shape[:2]
    max_dim = max(height, width)
    if max_dim < 1500:
        scale = 1500 / max_dim
        cv_image = cv2.resize(
            cv_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC
        )

    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    thresh = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=15,
    )

    return thresh


def extract_text_from_image(processed_image: np.ndarray) -> str:
    """Run EasyOCR on a preprocessed image and return concatenated text."""
    reader = _get_reader()
    results = reader.readtext(processed_image, detail=0, paragraph=True)
    text = "\n".join(results).strip()
    return text


def process_prescription_image(image_bytes: bytes) -> Tuple[str, bool]:
    """
    Full pipeline: bytes -> cv2 image -> preprocess -> OCR -> text.
    Returns (extracted_text, success_flag).
    """
    try:
        cv_image = bytes_to_cv2_image(image_bytes)
    except Exception:
        return "", False

    try:
        processed = preprocess_image(cv_image)
    except Exception:
        processed = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    try:
        text = extract_text_from_image(processed)
    except Exception:
        return "", False

    if not text:
        return "", False

    return text, True


def get_processed_preview(image_bytes: bytes) -> np.ndarray:
    """Utility for the frontend to display the processed image (grayscale/threshold)."""
    cv_image = bytes_to_cv2_image(image_bytes)
    return preprocess_image(cv_image)
