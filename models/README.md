# EasyOCR 모델 준비

앱은 이 폴더의 `craft_mlt_25k.pth`, `korean_g2.pth`를 CPU로 읽습니다.
이번 로컬 납품 폴더에는 기존 PC 캐시에서 복사한 두 모델이 준비되어 있습니다.
대용량 모델은 Git에 커밋하지 않습니다. 새 PC는 README의 온라인 준비 명령을 먼저 실행하세요.
앱에서는 `download_enabled=False`이므로 모델이 없을 때 네트워크 다운로드를 시도하지 않고 직접 입력을 안내합니다.
`OCR_MODEL_DIR` 환경 변수로 별도 준비된 모델 폴더도 지정할 수 있습니다.
