# 다른 Windows 노트북에서 실행하기

## 준비물
- Windows + Python 3.13 (검증된 버전은 3.13.14). 설치 시 "Add python.exe to PATH" 체크.
- 첫 설치에만 인터넷 필요.

## 옮기기
1. `senior-health-claim-checker` 폴더를 **`.venv` 폴더 제외**하고 ZIP으로 묶어 전달.
2. 받는 PC에서 압축 해제.
3. `models` 폴더의 `.pth` 파일 2개가 ZIP에 들어 있으면 모델 다운로드를 건너뜀(없으면 setup.bat이 자동 다운로드).

## 실행
1. `setup.bat` 더블클릭 (처음 1번, 몇 분 걸림)
2. `run.bat` 더블클릭 → 브라우저에서 http://127.0.0.1:8518

## 현장 체험 (같은 와이파이의 폰으로 접속)
- `run.bat lan` 으로 실행 → 폰에서 `http://<노트북 IP>:8518`
- IP는 명령 창에서 `ipconfig`의 IPv4 주소. 방화벽 창은 "개인 네트워크"만 허용.
- 끝나면 창을 닫아 종료.

## 문제 해결
- `Python not found`: Python 3.13 설치 후 새 창에서 다시.
- `pip install failed`: 인터넷 연결 확인 후 setup.bat 재실행.
- OCR이 안 되면 앱의 직접 입력을 사용.
