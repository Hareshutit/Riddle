from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.db.models import Count, Sum

static_url = settings.STATIC_URL

class ProfileManager(models.Manager):
    def top_users(self, count=5):
        return self.annotate(n_answers=Count('answer')).order_by('-n_answers')[:count]


class Profile(models.Model):
    avatar = models.ImageField(null=True, blank=True, verbose_name='Profile avatar',
                               default=static_url+"images/default.svg' %}")

    user = models.OneToOneField(to=User, related_name='profile', on_delete=models.CASCADE, null=False)

    objects = ProfileManager()

    def __str__(self):
        return self.user.username


class TagManager(models.Manager):
    def top_tags(self, count=5):
        return self.annotate(n_questions=Count('question')).order_by('-n_questions')[:count]


class Tag(models.Model):
    name = models.CharField(max_length=32, verbose_name='Tag name', unique=True)

    objects = TagManager()

    def __str__(self):
        return self.name


class ReputationManager(models.Manager):
    use_for_related_fields = True

    def likes(self):
        return self.get_queryset().filter(reputation__gt=0).aggregate(Sum('reputation')).get('reputation__sum') or 0

    def dislikes(self):
        return self.get_queryset().filter(reputation__lt=0).aggregate(Sum('reputation')).get('reputation__sum') or 0

class Reputation(models.Model):
    LIKE = 1
    DISLIKE = -1

    VOTES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]

    reputation = models.SmallIntegerField(verbose_name='Reputation', choices=VOTES)

    profile = models.ForeignKey(to=Profile, verbose_name='Profile', related_name='reputation', on_delete=models.CASCADE)

    content_type = models.ForeignKey(to=ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = ReputationManager()

    class Meta:
        unique_together = ('profile', 'content_type', 'object_id')


class QuestionManager(models.Manager):
    def new(self):
        return self.order_by('-pub_date')

    def hot(self):
        return self.order_by('-rating')

    def by_tag(self, tag):
        return self.filter(tags__name=tag)

    def by_id(self, id):
        return self.filter(id=id)


class Question(models.Model):
    title = models.CharField(max_length=256, verbose_name='Question title', blank=False)
    text = models.TextField(verbose_name='Question text', blank=False)
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Question publish date')
    rating = models.IntegerField(default=0)

    profile = models.ForeignKey(to=Profile, related_name='question', null=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(to=Tag, related_name='question', blank=True)
    reputations = GenericRelation(to=Reputation, related_query_name='question')

    objects = QuestionManager()

    def __str__(self):
        return self.title


class AnswerManager(models.Manager):
    def by_question(self, question_id):
        return self.filter(question_id=question_id)

class Answer(models.Model):
    text = models.TextField(verbose_name='Answer text', blank=False)
    correct = models.BooleanField(default=False, verbose_name='Answer correct')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Answer publish date')
    rating = models.IntegerField(default=0)

    profile = models.ForeignKey(to=Profile, related_name='answer', null=True, on_delete=models.SET_NULL)
    question = models.ForeignKey(to=Question, related_name='answer', on_delete=models.CASCADE)
    reputations = GenericRelation(to=Reputation, related_query_name='answer')

    objects = AnswerManager()

    def __str__(self):
        return self.text