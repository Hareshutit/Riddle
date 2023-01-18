from django.core.management.base import BaseCommand
from questions.models import Question, Profile, Reputation, Tag, Answer
from django.contrib.auth.models import User


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        Question.objects.all().delete()
        Answer.objects.all().delete()
        Reputation.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.all().delete()
        Tag.objects.all().delete()