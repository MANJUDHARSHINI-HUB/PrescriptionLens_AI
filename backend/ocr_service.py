"""
OCR Service
Uses OpenCV preprocessing and EasyOCR for text extraction.
"""

import io
from typing import Tuple

import cv2
import numpy as np
from PIL import Image

_reader = None


def _get_reader():
    global _reader

    if _reader is None:
        import easyocr

        _reader = easyocr.Reader(
            ["en"],
            gpu=False,
            verbose=False
        )

    return _reader


def bytes_to_cv2_image(image_bytes: bytes) -> np.ndarray:
    pil_image = Image.open(
        io.BytesIO(image_bytes)
    ).convert("RGB")

    np_image = np.array(pil_image)

    return cv2.cvtColor(
        np_image,
        cv2.COLOR_RGB2BGR
    )


def preprocess_image(cv_image: np.ndarray) -> np.ndarray:

    height, width = cv_image.shape[:2]

    # Keep image reasonably small for Render CPU
    max_dim = max(height, width)

    if max_dim > 1600:
        scale = 1600 / max_dim

        cv_image = cv2.resize(
            cv_image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_AREA
        )

    gray = cv2.cvtColor(
        cv_image,
        cv2.COLOR_BGR2GRAY
    )

    return gray


def extract_text_from_image(
    processed_image: np.ndarray
) -> str:

    reader = _get_reader()

    results = reader.readtext(
        processed_image,
        detail=0,
        paragraph=True
    )

    return "\n".join(results).strip()


def process_prescription_image(
    image_bytes: bytes
) -> Tuple[str, bool]:

    try:
        cv_image = bytes_to_cv2_image(image_bytes)
        processed = preprocess_image(cv_image)

        text = extract_text_from_image(processed)

        if not text:
            return "", False

        return text, True

    except Exception as e:
        print("OCR ERROR:", e)
        return "", False


def get_processed_preview(
    image_bytes: bytes
) -> np.ndarray:

    cv_image = bytes_to_cv2_image(image_bytes)

    return preprocess_image(cv_image)