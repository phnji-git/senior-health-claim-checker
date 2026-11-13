"""Run once while online; the app itself never downloads models."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.ocr import MODEL_DIR
import easyocr
MODEL_DIR.mkdir(parents=True,exist_ok=True)
easyocr.Reader(['ko','en'],gpu=False,model_storage_directory=str(MODEL_DIR),
               user_network_directory=str(MODEL_DIR/'user_network'),download_enabled=True)
print('Models ready:',MODEL_DIR)
