"""B의 EasyOCR CPU 구현. 모델/패키지 오류도 직접 입력으로 복구한다."""
import os
from pathlib import Path
from functools import lru_cache
# 이 값보다 신뢰도가 낮은 글자 조각은 "다시 확인할 부분"으로 알려 준다.
# 합성 이미지 3장 기준: 틀린 조각 0.32~0.58, 맞은 조각 0.62 이상. 실제 광고로 다시 맞출 것.
LOW_CONF = 0.6
MODEL_DIR =Path(os.environ.get('OCR_MODEL_DIR', Path(__file__).resolve().parents[1] / 'models'))

@lru_cache(maxsize=1)
def get_reader():
    import easyocr
    return easyocr.Reader(['ko','en'], gpu=False, verbose=False,
                          model_storage_directory=str(MODEL_DIR),
                          user_network_directory=str(MODEL_DIR / 'user_network'),
                          download_enabled=False)

def read_text(image_bytes):
    fail = {'text':'', 'status':'needs_review', 'error':''}
    try:
        if not image_bytes:
            return fail | {'error':'empty_image'}
        import cv2
        import numpy as np
        img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return fail | {'error':'invalid_image'}
        parts = get_reader().readtext(img)
        if not parts:
            return fail | {'error':'empty_result'}
        text = ' '.join(p[1].strip() for p in parts if p[1].strip())
        conf = sum(float(p[2]) for p in parts)/len(parts)
        return {'text':text,'status':'ok' if len(text.replace(' ',''))>=5 and conf>=.5 else 'needs_review',
                'confidence':conf,'error':'',
                'low_conf':[p[1].strip() for p in parts if p[1].strip() and float(p[2])<LOW_CONF]}
    except Exception as e:
        return fail | {'error':type(e).__name__}
