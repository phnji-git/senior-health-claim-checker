# 건강기능식품 광고 확인 도우미

광고 캡처의 문구를 읽어 식약처 공식 기능성 표시와 나란히 비교하고, 출처 링크와 확인일을 보여 주는 학습용 앱입니다.
"진짜/가짜", "불법/사기"는 판정하지 않습니다. 제출일 2026-11-18.

## 실행 방법 (Windows, Python 3.11)

프로젝트 폴더에서 PowerShell로 한 줄씩 실행합니다.

```
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

브라우저에서 `localhost:8501`이 열립니다.

## 폴더

- `app.py` 화면 / `src/` 기능 코드 / `data/processed/` CSV / `tests/` 테스트 / `docs/` 기록

## 팀 규칙

- 자기 파일만 수정, 자기 브랜치에서 Commit → Push → Pull Request. 병합은 팀장.
- API 키, 개인 사진, 실제 광고 캡처는 올리지 않습니다.
