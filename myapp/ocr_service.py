import threading
import time
import pyautogui
import cv2
import numpy as np
import easyocr
from collections import deque

# — 전역 설정 —

ROI = {'x': 0, 'y': 0, 'w': 100, 'h': 50}    # 초기 ROI 값 (views.set_rois / set_roi 로 덮어씌워집니다)
SUB_BUFFER = deque(maxlen=50)               # 최근 OCR 결과를 저장

# EasyOCR 리더 (한 번만 생성)
reader = easyocr.Reader(['ko','en'], gpu=False)

# 내부 OCR 루프
def _ocr_loop():
    prev_txt = ''
    while True:
        # 1) 지정된 영역 스크린샷
        r = ROI
        img = pyautogui.screenshot(region=(r['x'], r['y'], r['w'], r['h']))
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # 2) 전처리 (그레이스케일 → 이진화 → 확대)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        big = cv2.resize(th, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

        # 3) OCR 수행
        texts = reader.readtext(big, detail=0)
        txt = ' '.join(texts).strip()

        # 4) 중복 방지 + SUB_BUFFER 추가
        if txt and txt != prev_txt and len(txt) > 2:
            SUB_BUFFER.append({
                'time': time.time(),  # 나중에 timestamp 기준 병합에 사용
                'text': txt
            })
            prev_txt = txt

        time.sleep(0.7)  # 700ms 간격

# 백그라운드 스레드 관리
_thread = None

def start_ocr_service():
    """
    백그라운드에서 _ocr_loop 를 실행합니다.
    이미 실행 중이면 중복으로 시작하지 않습니다.
    """
    global _thread
    if _thread is None or not _thread.is_alive():
        _thread = threading.Thread(target=_ocr_loop, daemon=True)
        _thread.start()
