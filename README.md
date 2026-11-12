# 건강기능식품 광고 확인 도우미

광고 캡처의 문구를 읽어 식약처 공식 기능성 표시와 나란히 비교하고, 출처 링크와 확인일을 보여 주는 학습용 앱입니다.
"진짜/가짜", "불법/사기"는 판정하지 않습니다. 제출일 2026-11-18.

## 현재 PC에서 실행 (검증 환경: Windows / Python 3.13.14 / CPU)

현재 작업 위치: `C:\Users\USER\etc\bioinfo\senior-health-claim-checker`. 브랜치: `feature/ui`.

프로젝트 폴더에서 PowerShell로 한 줄씩 실행합니다.

```
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8518 --browser.gatherUsageStats false
```

브라우저에서 http://127.0.0.1:8518 을 엽니다. 기존 8501 준비 화면과 구별하기 위해 8518을 사용합니다.
현재 저장소에는 `.venv`와 두 OCR 모델이 준비되어 있습니다. API 키 없이 실행합니다.
현재 `.venv`는 기존 설정을 `pyvenv.before-integration.cfg`로 백업한 뒤 `include-system-site-packages = true`로 설정해 이 PC의 OCR 패키지를 재사용하므로 다른 PC로 `.venv`를 복사하지 마세요.

## 새 PC 설치와 최초 모델 준비

실제로 검증한 Python은 3.13.14입니다. 팀 가이드의 3.11은 이 PC에 설치되어 있지 않아 검증하지 못했습니다.
아래 고정 버전은 현재 3.13 환경의 실행 버전이며 3.11 호환을 보증하지 않습니다.
공식 Python Windows 설치 후 프로젝트 폴더에서 실행하세요.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# OCR을 사용할 때만 추가 설치
.\.venv\Scripts\python.exe -m pip install -r requirements-ocr.txt
# 인터넷 연결 상태에서 1회 모델 준비 (API 키 불필요)
.\.venv\Scripts\python.exe scripts/prepare_models.py
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8518 --browser.gatherUsageStats false
```

실행 정책을 바꾸거나 가상환경을 활성화할 필요 없이 위 Python 경로를 직접 사용하세요.
앱은 `models/craft_mlt_25k.pth`, `models/korean_g2.pth`를 읽으며 실행 중 자동 다운로드하지 않습니다.
현재 모델은 이 PC의 기존 EasyOCR 캐시에서 복사해 실제 인식까지 검증했습니다. Git에는 대용량 모델이 포함되지 않습니다.
모델이 없거나 OCR 설치가 실패해도 직접 문구 입력은 가능합니다. 모든 조회·비교는 저장된 CSV를 사용합니다.
출처 링크를 열 때만 공식 사이트로 이동합니다. 업로드 이미지·문구를 외부 OCR/API로 보내거나 파일로 저장하지 않습니다.

## 사용 순서

1. JPG/PNG를 업로드하고 미리보기를 확인합니다. 또는 광고 문구를 직접 입력합니다.
2. `사진에서 글자 읽기`를 누르면 인식 문구가 편집 상자에 나타납니다. 오타를 반드시 고칩니다.
3. `이 문구로 제품 찾기` → 후보의 제품명·업체명·신고번호를 포장과 대조합니다.
4. 제품을 직접 선택하고 `선택한 제품으로 비교`를 누릅니다. 후보는 자동 확정되지 않습니다.
5. 광고와 공식 원문, 확인할 표현, 출처 URL과 확인일을 함께 봅니다.

제품을 찾지 못하면 정확한 제품명 또는 신고번호로 다시 검색하세요. 최대 10개 후보만 표시합니다.
신고 목록 후보는 원문 검수 제품과 구분합니다. 원문/URL/확인일이 없으면 결측 상태를 표시하며 공식 검색으로 안내합니다.
`matched`는 관련 문구를 찾았다는 내부 상태이며, 의미 동일·효과·위법 여부를 판정하지 않습니다.
팀의 쉬운 설명은 검수 전 초안으로 접힌 별도 영역에 표시합니다. 공식 표시와 같은 지위가 아닙니다.

## 재현 가능한 검증

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/validate_integration.py
.\.venv\Scripts\python.exe scripts/validate_ocr.py
```

- D v3 기준: 상태 20/20, 기대 제품 ID 17/17, 후보 Top-1 17/17, 기대 태그 포함 20/20.
- 출처 상태 20/20: URL·확인일 확보 사례 17건, 미검색 2건·신고 목록만 있는 1건의 결측 상태 3건. 20건 모두 출처 확보라는 뜻이 아닙니다.
- 자동 시험 20개 통과. 표현 탐지 회귀 7개(반대·부정 문장, 100%·100프로, 보장, 질병명, 치유, 부작용 없음), 오탐 방지 2개(부작용 없이·걱정 없는), 신고번호 완전 일치 1개와 후보 확정·자료 범위·OCR 실패·화면 복구를 포함합니다.
- 실제 이미지 OCR 7장: 상태 7/7, 기대 제품 ID가 있는 5건 5/5, 태그 7/7. 7장 모두 오인식이 있습니다.
- 브라우저: 정상 PNG 업로드→OCR→수정→선택→출처, 직접 입력, 미검색, 공식 자료 없음, 빈 OCR→직접 입력 복구를 확인했습니다.
- 합성 사례에 맞춰 규칙을 보정한 개발 회귀 결과입니다. 독립 평가나 사람 대상 사용성 결과가 아닙니다.

상세: `docs/test_results.csv`, `docs/ocr_test_results.csv`, `docs/integration_report.md`, `docs/usability_protocol.md`.

## 실패 지점과 재현

- `py -3.11` / `py -0p`: 이 PC의 런처는 설치된 Python을 찾지 못했습니다. 실제 `python`은 Python313 경로의 3.13.14입니다.
- 제한 실행 환경의 `python -m venv ...`: `ensurepip` 비정상 종료, 이어서 `No module named pip`. 승인된 일반 실행으로 같은 사본 안의 venv 생성·설치를 완료했습니다.
- 제한 실행 환경의 서버·AppTest는 대기 상태가 지속되어 중단했습니다. 일반 실행에서는 서버 기동과 12개 시험이 완료됐습니다.
- `OCR_MODEL_DIR`를 비어 있는 폴더로 지정하고 서버를 새로 시작한 뒤 사진을 읽으면 모델 초기화 실패를 재현할 수 있습니다. 앱은 직접 입력을 안내합니다.
- `data/synthetic/blank.png`를 업로드하고 OCR를 누르면 `empty_result`. 텍스트 상자에 문구를 입력하면 계속 진행합니다.
- 코드 변경 후에는 서버를 Ctrl+C로 종료하고 다시 실행하세요. 모듈을 바꾼 뒤 브라우저 새로고침만 하면 이전 모듈이 남을 수 있습니다.
- PyTorch의 CPU pin_memory·양자화 경고는 인식 완료를 막지 않았습니다. 최초 제한 실행 pytest 종료 후 pyreadline 콘솔 정리 오류가 있었으나 테스트 종료 코드는 0이었고, 일반 실행 재시험은 정상 완료됐습니다.
- 서버 재시작 때 Windows 소켓 `WinError 10054` 종료 로그가 있었으며 새 서버 기동·비교는 정상입니다.

## 데이터·공통 함수

앱은 프로젝트 기준 상대 경로 `data/processed`만 읽습니다. 외부 XLSX나 I0030 원본 경로에 의존하지 않습니다.
공식 CSV 24개·125행의 원문은 보존하고 확인일만 기존 `docs/data_sources.md`의 전체 대조 기록(2026-11-11)에 맞췄습니다.
신고 목록 `registry_index.csv`는 후보 검색에만 사용하고 원료용 표시 행을 제외합니다. 목록의 상세 URL·확인일은 추정해서 채우지 않습니다.
원본 XLSX와 D v3의 읽기/변환에는 pandas·openpyxl을 사용했으며 앱 실행에는 openpyxl이 필요하지 않습니다.
옛 `data/synthetic/sample_ads/synthetic_cases.csv`는 오래된 제품 ID가 있어 보존만 합니다. 활성 시험 파일은 `data/processed/synthetic_cases.csv`입니다.

`analyze_claim(ad_text, product_id=None)`는 가이드 필드에 `product_id`, `official_claim_rows`, `selection_required`, `review_evidence`를 추가합니다.
제품 미선택 시 후보가 있으면 `needs_review` + `selection_required=True`이고 원문 비교를 하지 않습니다.
제품 선택 후에만 비교합니다. 유사도는 후보/관련 문구 검색에 사용하며 부정·단정·치료 표현이 있으면 `matched`를 차단합니다.

OCR 구현은 B의 실제 EasyOCR 1.7.2를 사용합니다. 가이드의 PaddleOCR는 설치하지 않습니다.
참고 문서: [Streamlit 업로더](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader), [EasyOCR 공식 저장소](https://github.com/JaidedAI/EasyOCR).

## 폴더

- `app.py` 화면 / `src/` 기능 코드 / `data/processed/` CSV / `tests/` 테스트 / `docs/` 기록

## 팀 규칙

- 자기 파일만 수정, 자기 브랜치에서 Commit → Push → Pull Request. 병합은 팀장.
- API 키, 개인 사진, 실제 광고 캡처는 올리지 않습니다.
