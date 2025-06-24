from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from myapp.models import Events, Memo

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

# 메인 페이지 나누기
def home(request):
    return render(request, 'home.html')

def index(request):
    return render(request, 'index.html')

# 메인 화면 메모기능 추가
def home(request):
    # POST(폼 제출)이 들어오면 새 메모 생성
    if request.method == 'POST':
        title   = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            Memo.objects.create(title=title, content=content)
            return redirect('home')

    memos = Memo.objects.all()   # ordering = ['created_at'] 덕분에 생성 순 정렬
    return render(request, 'home.html', {
        'memos': memos,
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