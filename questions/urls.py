from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.index, name='index'),
    path('tag/<str:tag>/', views.tag, name='list_with_tag'),
    path('hot/', views.hot, name='hot_list'),
    path('page/<int:page>/', views.index, name='list_page'),
    path('ask/', views.new_question, name='new_question'),
    path('question/<int:id>/', views.question, name='question'),
    path('login/', views.sign_in, name='sign_in'),
    path('signup/', views.sign_up, name='sign_up'),
    path('logout/', views.logout, name='logout'),
    path('settings/', views.settings, name='settings')
]
