from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from myapp.models import Events, Memo, Bookmark

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

#자막 추출 페이지
def auto_subtitle(request):
    return render(request, 'auto_subtitle.html')

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