from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from myapp.models import Events, Memo, Bookmark

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

import pytesseract

import json
from django.views.decorators.http import require_POST

import cv2
import numpy as np
import pyautogui
import easyocr
#OCR

reader = easyocr.Reader(['ko','en'], gpu=False)
prev_text = ''

pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

# Create your views here.
def index(request):
    all_events = Events.objects.all()
    context = {
        "events":all_events,
    }
    return render(request, 'index.html',context)

def all_events(request):
    all_events = Events.objects.all()
    out = []
    for event in all_events:
        out.append({
            'title': event.name,
            'id': event.id,
            'start': event.start.strftime("%m/%d/%Y, %H:%M:%S"),
            'end': event.end.strftime("%m/%d/%Y, %H:%M:%S"),
        })

    return JsonResponse(out, safe=False)

def add_event(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    event = Events(name=str(title), start=start, end=end)
    event.save()
    data = {}
    return JsonResponse(data)

def update(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.start = start
    event.end = end
    event.name = title
    event.save()
    data = {}
    return JsonResponse(data)

def remove(request):
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.delete()
    data = {}
    return JsonResponse(data)


# 메인 화면 메모기능 추가
def home(request):
    # 1) POST: 새 메모 등록
    if request.method == 'POST' and 'title' in request.POST:
        Memo.objects.create(
            title   = request.POST['title'],
            content = request.POST['content']
        )
        return redirect('home')

    # 2) GET: 메모와 즐겨찾기 조회
    memos     = Memo.objects.all()
    bookmarks = Bookmark.objects.all()

    # ─── 여기가 핵심: 딕셔너리 } 와 함수 호출 ) 를 닫아줍니다 ───
    return render(request, 'home.html', {
        'memos':     memos,
        'bookmarks': bookmarks,
    })

def memo_detail(request, memo_id):
    memo = get_object_or_404(Memo, id=memo_id)
    return render(request, 'memo_detail.html', {
        'memo': memo,
    })

#메모 삭제
def memo_delete(request, memo_id):
    memo = get_object_or_404(Memo, id=memo_id)
    if request.method == 'POST':
        memo.delete()
        return redirect('home')

#메모 수정
def memo_edit(request, memo_id):
    memo = get_object_or_404(Memo, id=memo_id)
    if request.method == 'POST':
        title   = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            memo.title   = title
            memo.content = content
            memo.save()
    # 수정 후에는 상세 화면으로 돌아갑니다
    return redirect('memo_detail', memo_id=memo.id)


#메인 화면 북마크
def add_bookmark(request):
    if request.method == 'POST':
        name = request.POST.get('bookmark_name')
        url  = request.POST.get('bookmark_url')
        if name and url:
            Bookmark.objects.create(name=name, url=url)
    return redirect('home')

def delete_bookmark(request, bookmark_id):
    bm = get_object_or_404(Bookmark, id=bookmark_id)
    bm.delete()
    return redirect('home')

#auto_subtitle 기능 추가
ocr_started = False

def auto_subtitle(request):
    return render(request, 'auto_subtitle.html')

def subtitles_api(request):
    # 가장 최근 BUFFER_SIZE 개 자막을 내려줍니다
    return JsonResponse({'subtitles': SUB_BUFFER})

@csrf_exempt
def start_ocr(request):
    """
    클라이언트에서 POST 요청이 들어오면
    ocr_service.py 의 OCR 루프를 시작합니다.
    """
    start_ocr_service()
    return JsonResponse({'status':'ocr started'})

def clear_subtitles(request):
    """
    클라이언트에서 호출하면 OCR 서비스가 쌓아둔 SUB_BUFFER를 비웁니다.
    """
    SUB_BUFFER.clear()
    return JsonResponse({'status': 'cleared'})

def set_rois(request):
    """
    클라이언트에서 보낸 두 개의 ROI 좌표를 ocr_service.ROI 에 저장합니다.
    """
    if request.method != 'POST':
        return JsonResponse({'error':'POST만 허용'}, status=405)

    try:
        body = json.loads(request.body)
        rois = body.get('rois', [])

        if len(rois) != 2:

            return JsonResponse({'error': 'rois 배열에 2개 요소 필요'}, status=400)

        # OCR 서비스 모듈을 통째로 import 해서 전역 ROIS에 덮어쓰기

        import myapp.ocr_service as ocr_service
        ocr_service.ROIS = rois

        return JsonResponse({'status':'ok'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def set_roi(request):
    """
    클라이언트에서 보낸 { x,y,w,h } 로 ocr_service.ROI를 덮어씌웁니다.
    """
    from .ocr_service import ROI
    data = json.loads(request.body)
    ROI['x'] = data['x']
    ROI['y'] = data['y']
    ROI['w'] = data['w']
    ROI['h'] = data['h']
    return JsonResponse({'status':'ok'})

@csrf_exempt
def ocr_poll(request):
    """
    GET 파라미터로 x,y,w,h를 받아
    해당 영역만 스크린샷→OCR 후 변경된 텍스트를 JSON으로 리턴
    """
    global prev_text

    try:
        x = int(request.GET.get('x', 0))
        y = int(request.GET.get('y', 0))
        w = int(request.GET.get('w', 0))
        h = int(request.GET.get('h', 0))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'invalid coords'}, status=400)

    # ——— 여기부터 변경 ———
    # padding 넣고 싶으면 pad 만큼 좌표를 확장
    pad = 10
    rx = max(x - pad, 0)
    ry = max(y - pad, 0)
    rw = w + pad*2
    rh = h + pad*2

    # region=(left, top, width, height) 파라미터로 바로 잘라오기
    img = pyautogui.screenshot(region=(rx, ry, rw, rh))
    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # 혹시 빈 이미지라면 빈 문자열만 반환
    if frame.size == 0:
        return JsonResponse({'text': ''})
    # ————— 변경 끝 —————

    # 전처리
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    blur = cv2.GaussianBlur(thresh, (3,3), 0)
    big = cv2.resize(blur, None, fx=2, fy=2,
                     interpolation=cv2.INTER_LINEAR)

    # OCR
    results = reader.readtext(big, detail=0)
    text = ''
    if results:
        candidate = " ".join(results).strip()
        if candidate and candidate != prev_text and len(candidate) > 3:
            prev_text = candidate
            text = candidate

    return JsonResponse({'text': text})



