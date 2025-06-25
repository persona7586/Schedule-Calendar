# myapp/consumers.py
import base64, cv2, numpy as np
from channels.generic.websocket import AsyncWebsocketConsumer
from easyocr import Reader

class OcrConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.reader = Reader(['ko','en'], gpu=False)
        print("🟢 OCR WebSocket 연결 수립")

    async def receive(self, text_data):
        # text_data = "data:image/jpeg;base64,..."
        print("📥 프레임 수신 (길이):", len(text_data))
        header, b64 = text_data.split(',', 1)
        img_data = base64.b64decode(b64)
        npimg    = np.frombuffer(img_data, np.uint8)
        frame    = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        blur = cv2.GaussianBlur(th, (3,3), 0)
        big  = cv2.resize(blur, None, fx=2, fy=2,
                          interpolation=cv2.INTER_LINEAR)

        results = self.reader.readtext(big, detail=0)
        print("🔍 OCR 결과:", results)
        if results:
            text = " ".join(results)
            await self.send(text)
