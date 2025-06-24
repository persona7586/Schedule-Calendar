"""
URL configuration for DjangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1) 메인(홈) 페이지
    path('', views.home, name='home'),
    # 2) 달력 페이지
    path('calendar/', views.index, name='calendar'),


    path('', views.index, name='index'),
    path('all_events/', views.all_events, name='all_events'),
    path('add_event/', views.add_event, name='add_event'),
    path('update/', views.update, name='update'),
    path('remove/', views.remove, name='remove'),

    #메인 페이지 메모 상세보기
    path('memo/<int:memo_id>/', views.memo_detail, name='memo_detail'),
    path('memo/<int:memo_id>/delete/',     views.memo_delete, name='memo_delete'),

]
