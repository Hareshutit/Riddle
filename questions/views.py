from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET, require_http_methods
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from questions.models import Question, Profile, Tag, Answer, Reputation
from questions.forms import RegistrationForm, LoginForm, QuestionForm, AnswerForm, SettingsForm

tag_list = Tag.objects.all()
top_tag = Tag.objects.top_tags()
top_author = Profile.objects.top_users()

def question_instance(question_list):
    question_objects = [{
        'id': question_list[i].id,
        'author': question_list[i].profile,
        'title': question_list[i].title,
        'body': question_list[i].text,
        'date_publicate': f'Дата публикации {question_list[i].pub_date}',
        'tags': [question_list[i].tags.all()[j] for j in range(len(question_list[i].tags.all()))],
        'count_answers': Answer.objects.by_question(question_list[i].id).count(),
        'likes_count': question_list[i].reputations.likes(),
        'dislikes_count': question_list[i].reputations.dislikes(),
    } for i in range(len(question_list))]
    return question_objects

def answers_instance(answer_list):
    answer_objects = [{
        'id': answer_list[i].id,
        'author': answer_list[i].profile,
        'text': answer_list[i].text,
        'date_publicate': f'Дата публикации {answer_list[i].pub_date}',
        'likes_count': answer_list[i].reputations.likes(),
        'dislikes_count': answer_list[i].reputations.dislikes(),
    } for i in range(len(answer_list))]
    return answer_objects

def paginate(object_list, request, per_page=5):
    items_paginator = Paginator(object_list, per_page)
    page_num = request.GET.get('page')
    page = items_paginator.get_page(page_num)
    return page

def index(request):
    template = 'questions/index.html'
    context = {
        'top_author': top_author,
        'tags_list': tag_list,
        'top_tag': top_tag,
        'page_obj': paginate(question_instance(Question.objects.new()), request)
    }
    return render(request, template, context)

def tag(request, tag: str):
    template = 'questions/index.html'
    context = {
        'top_author': top_author,
        'tags_list': tag_list,
        'top_tag': top_tag,
        'page_obj': paginate(question_instance(Question.objects.by_tag(tag)), request)
    }
    return render(request, template, context)

def hot(request):
    template = 'questions/index.html'
    context = {
        'top_author': top_author,
        'tags_list': tag_list,
        'top_tag': top_tag,
        'page_obj': paginate(question_instance(Question.objects.hot()), request)
    }
    return render(request, template, context)

@require_http_methods(['GET', 'POST'])
def question(request, id: int):
    print(request.user)
    template = 'questions/question.html'
    if request.method == 'GET':
        answer_form = AnswerForm()
    if request.method == 'POST':
        answer_form = AnswerForm(data=request.POST)
        if answer_form.is_valid():
            answer_form.save(request, id)
    context = {
        'form': answer_form,
        'question': question_instance(Question.objects.by_id(id))[0],
        'top_author': top_author,
        'top_tag': top_tag,
        'page_obj': paginate(answers_instance(Answer.objects.by_question(id)), request),
        'closed': False,
    }
    return render(request, template, context)

@require_http_methods(['GET', 'POST'])
def new_question(request):
    template = 'questions/new_question.html'
    if request.method == 'GET':
        question_form = QuestionForm()
    if request.method == 'POST':
        question_form = QuestionForm(data=request.POST)
        if question_form.is_valid():
            question_form.save(request)
    context = {
        'form': question_form,
        'top_author': top_author,
        'top_tag': top_tag,
    }
    return render(request, template, context)


def settings(request):
    template = 'questions/profile_update.html'
    if request.method == 'GET':
        edit_form = SettingsForm(instance=request.user)
    if request.method == 'POST':
        edit_form = SettingsForm(data=request.POST, files=request.FILES, instance=Profile.objects.get(user=request.user))
        if edit_form.is_valid():
            edit_form.save()
    context = {
        'form': edit_form,
        'top_author': top_author,
        'top_tag': top_tag,
    }
    return render(request, template, context)

def sign_in(request):
    template = 'questions/sign-in.html'
    if request.method == 'GET':
        login_form = LoginForm()
    if request.method == 'POST':
        login_form = LoginForm(data=request.POST)
        if login_form.is_valid():
            user = auth.authenticate(request=request, **login_form.cleaned_data)
            print(user)
            if user:
                auth.login(request, user)
                return redirect('/')
            else:
                login_form.add_error(None, "Неправильный логин или пароль")
                login_form.add_error('username', "")
                login_form.add_error('password', "")
    context = {
        'form': login_form,
        'top_author': top_author,
        'top_tag': top_tag,
    }
    return render(request, template, context)

@require_http_methods(['GET', 'POST'])
def sign_up(request):
    template = 'questions/sign-up.html'
    if request.method == 'GET':
        registration_form = RegistrationForm()
    if request.method == 'POST':
        registration_form = RegistrationForm(data=request.POST, files=request.FILES)
        if registration_form.is_valid():
            profile = registration_form.save()
            auth.login(request, profile.user)
            return redirect('/')
    context = {
        'form': registration_form,
        'top_author': top_author,
        'top_tag': top_tag,
    }
    return render(request, template, context = context)

@login_required(login_url='login', redirect_field_name='continue')
def logout(request):
    auth.logout(request)
    return redirect('/')