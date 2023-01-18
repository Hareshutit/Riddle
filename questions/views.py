from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET

from random import choice

from questions.models import Question, Profile, Tag, Answer, Reputation

tag_list = Tag.objects.all()
top_tag = Tag.objects.top_tags()
top_author = Profile.objects.top_users()
authorized = True

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
        'authorized': authorized,
        'top_author': top_author,
        'tags_list': tag_list,
        'top_tag': top_tag,
        'page_obj': paginate(question_instance(Question.objects.new()), request)
    }
    return render(request, template, context)

def tag(request, tag: str):
    template = 'questions/index.html'
    context = {
        'authorized': authorized,
        'top_author': top_author,
        'tags_list': tag_list,
        'top_tag': top_tag,
        'page_obj': paginate(question_instance(Question.objects.by_tag(tag)), request)
    }
    return render(request, template, context)

def hot(request):
    template = 'questions/index.html'
    context = {
        'authorized': authorized,
        'top_author': top_author,
        'tags_list': tag_list,
        'top_tag': top_tag,
        'page_obj': paginate(question_instance(Question.objects.hot()), request)
    }
    return render(request, template, context)

def question(request, id: int):
    template = 'questions/question.html'
    context = {
        'question': question_instance(Question.objects.by_id(id))[0],
        'top_author': top_author,
        'top_tag': top_tag,
        'authorized': authorized,
        'page_obj': paginate(answers_instance(Answer.objects.by_question(id)), request),
        'closed': False,
    }
    return render(request, template, context)

def new_question(request):
    template = 'questions/new_question.html'
    context = {
        'authorized': authorized,
    }
    return render(request, template, context)


def settings(request):
    template = 'questions/profile_update.html'
    context = {
        'authorized':authorized,
    }
    return render(request, template, context)

def sign_in(request):
    template = 'questions/sign-in.html'
    context = {
        'top_author': top_author,
        'top_tag': top_tag,
    }
    return render(request, template, context)


def sign_up(request):
    template = 'questions/sign-up.html'
    context = {
        'top_author': top_author,
        'top_tag': top_tag,
    }
    return render(request, template, context)

