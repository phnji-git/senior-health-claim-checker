"""광고 이미지에서 글자만 읽는다. 진짜/가짜, 불법 판정은 하지 않는다."""
import cv2
import easyocr
import numpy as np

MIN_CHARS = 5   # ponytail: 임시 기준값, 샘플 결과 보고 조정
MIN_CONF = 0.5  # 읽은 조각들의 평균 신뢰도 기준

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["ko", "en"], gpu=False, verbose=False)
    return _reader


def read_text(image_bytes) -> dict:
    fail = {"text": "", "status": "needs_review"}
    try:
        if not image_bytes:
            return fail
        img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return fail
        parts = _get_reader().readtext(img)
        if not parts:
            return fail
        text = " ".join(p[1].strip() for p in parts if p[1].strip())
        conf = sum(p[2] for p in parts) / len(parts)
        ok = len(text.replace(" ", "")) >= MIN_CHARS and conf >= MIN_CONF
        return {"text": text, "status": "ok" if ok else "needs_review"}
    except Exception:
        return fail


if __name__ == "__main__":
    # 간이 점검: 빈 입력, 깨진 이미지는 예외 없이 needs_review
    assert read_text(b"") == {"text": "", "status": "needs_review"}
    assert read_text(b"not an image") == {"text": "", "status": "needs_review"}
    print("empty/broken OK")
