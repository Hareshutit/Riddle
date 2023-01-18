from django.contrib import admin
from questions.models import Question, Answer, Profile, Tag, Reputation

admin.site.register(Profile)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Tag)
admin.site.register(Reputation)