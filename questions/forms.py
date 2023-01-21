
from django.core.exceptions import ValidationError

from django import forms
from django.core.validators import validate_email
from django.forms import CharField

from django.contrib.auth.models import User
from questions.models import Profile, Question, Tag, Answer

class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(), label='Почта:', required=True)
    password = forms.CharField(widget=forms.PasswordInput(render_value=True), min_length=8, label='Пароль:')
    password_check = forms.CharField(widget=forms.PasswordInput(render_value=True), label='Подтвердите пароль:')
    avatar = forms.ImageField(widget=forms.FileInput(), label='Аватар:', required=False)
    first_name = forms.CharField(widget=forms.TextInput(), min_length=1, label='Имя:', required=True)
    last_name = forms.CharField(widget=forms.TextInput(), min_length=1, label='Фамилия:', required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_check', 'first_name', 'last_name']

        labels = {
            'username': 'Логин:'
        }

        help_texts = {
            'username': None
        }

    def clean(self):
        if 'password' not in self.cleaned_data.keys() or 'password_check' not in self.cleaned_data.keys():
            return self.cleaned_data

        if self.cleaned_data['password'] != self.cleaned_data['password_check']:
            self.add_error('password_check', 'Пароли не совпадают')

        return self.cleaned_data

    def clean_username(self):
        data = self.cleaned_data['username']
        if User.objects.filter(username=data).exists():
            self.add_error('username', 'Пользователь с данным именем существует')
        return data

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            self.add_error('email', 'Пользователь с данной почтой уже существует')
        return data

    def save(self, **kwargs):
        avatar = None
        if 'avatar' in self.cleaned_data.keys():
            avatar = self.cleaned_data['avatar']

        self.cleaned_data.pop('password_check')
        self.cleaned_data.pop('avatar')
        user = User.objects.create_user(**self.cleaned_data)

        profile = Profile.objects.create(user=user)
        if avatar:
            profile.avatar = avatar
        profile.save()
        return profile

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(), label='Имя пользователя:', required=True)
    password = forms.CharField(widget=forms.PasswordInput(render_value=True), label='Пароль:')

class QuestionForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(), min_length=1, max_length=64, label='Заголовок:', required=True)
    tags = forms.CharField(widget=forms.TextInput(), min_length=1, max_length=64, label='Теги:', required=True)
    text = forms.CharField(widget=forms.Textarea(), min_length=1, max_length=256, label='Вопрос:', required=True)

    class Meta:
        model = Question
        fields = ['title', 'tags', 'text']

    def save(self, request, **kwargs):
        quest = super().save(commit=False)
        quest.profile = Profile.objects.get(user=request.user)
        quest.save()

        tags = self.cleaned_data['tags']
        tag_list = tags.split()
        for tag in tag_list:
            quest.tags.add(Tag.objects.get_or_create(name=tag)[0].id)

        quest.save()
        return quest

class AnswerForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(), min_length=1, max_length=256, label='Ответ:', required=True)

    class Meta:
        model = Answer
        fields = ['text']

    def save(self, request, q_id: int, **kwargs):
        answer = super().save(commit=False)
        answer.profile = Profile.objects.get(user=request.user)
        answer.question = Question.objects.by_id(q_id)[0]
        answer = super().save()
        
        return answer

class SettingsForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(), label='Почта:', required=False)
    password = forms.CharField(widget=forms.PasswordInput(render_value=True), min_length=8, label='Пароль:')
    password_check = forms.CharField(widget=forms.PasswordInput(render_value=False), label='Подтвердите пароль:')
    avatar = forms.ImageField(widget=forms.FileInput(), label='Аватар:', required=False)
    first_name = forms.CharField(widget=forms.TextInput(), min_length=1, label='Имя:', required=False)
    last_name = forms.CharField(widget=forms.TextInput(), min_length=1, label='Фамилия:', required=False)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_check', 'first_name', 'last_name']

        labels = {
            'username': 'Логин:'
        }

        help_texts = {
            'username': None
        }

    def clean(self):
        if 'password' not in self.cleaned_data.keys() or 'password_check' not in self.cleaned_data.keys():
            return self.cleaned_data

        if self.cleaned_data['password'] != self.cleaned_data['password_check']:
            self.add_error('password_check', 'Пароли не совпадают')

        return self.cleaned_data
