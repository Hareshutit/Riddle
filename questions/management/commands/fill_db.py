from django.core.management.base import BaseCommand
from questions.models import Question, Profile, Tag, Answer, Reputation
from django.contrib.auth.models import User

from faker import Faker, exceptions
import random

DEFAULT_N_USERS = 1
DEFAULT_N_QUESTIONS = 10
DEFAULT_N_ANSWERS = 100
DEFAULT_N_TAGS = 1
DEFAULT_N_LIKES = 180

WORD_LIST = ('cat', 'dog', 'burito', 'vine', 'mems', 'python', 'Go', 'OCaml', 'Haskell', 'anacondaz')


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.faker = Faker()

    def add_arguments(self, parser):
        parser.add_argument('--ratio', type=int)

    def handle(self, **options):
        ratio = int(options['ratio']) if options['ratio'] else 10

        self.users_gen(ratio * DEFAULT_N_USERS)
        self.tags_gen(ratio * DEFAULT_N_TAGS)
        self.questions_gen(ratio * DEFAULT_N_QUESTIONS)
        self.answers_gen(ratio * DEFAULT_N_ANSWERS)
        self.reputations_gen(ratio * DEFAULT_N_LIKES)

    def users_gen(self, count):
        print("Users generating...")
        users = [None] * count
        profiles = [None] * count

        for i in range(count):
            user = User(username=self.faker.unique.user_name(), first_name=self.faker.first_name(),
                        last_name=self.faker.last_name(), email=self.faker.email())
            user.set_password(raw_password=self.faker.password())

            users[i] = user
            profiles[i] = Profile(user=user, avatar=f'/static/images/({random.randint(1, 20)}).jpg')
        User.objects.bulk_create(users)
        Profile.objects.bulk_create(profiles)
        print('Success.')

    def tags_gen(self, count):
        print("Tags generating...")
        word = [None] * 2
        tags = [None] * count
        used_words = []
        for i in range(count):
            print(i)
            for j in range(2):
                word[j] = random.choice(WORD_LIST)
            while word in used_words:
                for j in range(2):
                    word[j] = random.choice(WORD_LIST)
            used_words.append(word.copy())

            tags[i] = Tag(name="".join(word))

        Tag.objects.bulk_create(tags)
        print("Success.")

    def questions_gen(self, count):
        print("Questions generating...")
        prof_min_id = Profile.objects.order_by('id')[0].id
        prof_max_id = Profile.objects.order_by('-id')[0].id
        tag_min_id = Tag.objects.order_by('id')[0].id
        tag_max_id = Tag.objects.order_by('-id')[0].id

        questions = [None] * count
        for i in range(count):
            print(i)
            title = self.faker.paragraph(1)[:-1] + '?'
            text = self.faker.paragraph(random.randint(5, 20))
            profile_id = random.randint(prof_min_id, prof_max_id)

            questions[i] = Question(text=text, title=title, profile_id=profile_id)
        questions = Question.objects.bulk_create(questions)
        print("Success.")

        print("Adding tags to questions...")
        tags = [None] * 10
        for i in range(count):
            print(i)
            n_tags = random.randint(1, 5)
            for j in range(n_tags):
                tags[j] = Tag.objects.get(id=random.randint(tag_min_id, tag_max_id))
            questions[i].tags.add(*tags[:n_tags])
            questions[i].save()
        print("Success.")

    def answers_gen(self, count):
        print("Answers generating...")
        prof_min_id = Profile.objects.order_by('id')[0].id
        prof_max_id = Profile.objects.order_by('-id')[0].id
        que_min_id = Question.objects.order_by('id')[0].id
        que_max_id = Question.objects.order_by('-id')[0].id

        answers = [None] * count
        for i in range(count):
            print(i)
            text = self.faker.paragraph(random.randint(5, 20))
            profile_id = random.randint(prof_min_id, prof_max_id)
            question_id = random.randint(que_min_id, que_max_id)

            answers[i] = Answer(text=text, profile_id=profile_id, question_id=question_id)
        Answer.objects.bulk_create(answers)
        print("Success.")

    def reputations_gen(self, count):
        prof_min_id = Profile.objects.order_by('id')[0].id
        prof_max_id = Profile.objects.order_by('-id')[0].id
        que_min_id = Question.objects.order_by('id')[0].id
        que_max_id = Question.objects.order_by('-id')[0].id

        n_q_likes = count // 4
        q_likes = [None] * n_q_likes
        used_pairs = []
        print('Question likes generating...')
        for j in range(n_q_likes):
            print(j)
            profile_id = random.randint(prof_min_id, prof_max_id)
            question_id = random.randint(que_min_id, que_max_id)
            while (profile_id, question_id) in used_pairs:
                profile_id = random.randint(prof_min_id, prof_max_id)
                question_id = random.randint(que_min_id, que_max_id)
            used_pairs.append((profile_id, question_id))

            question = Question.objects.get(id=question_id)
            question.rating += 1
            question.save()

            q_likes[j] = Reputation(reputation=1, profile_id=profile_id, content_object=question)
        Reputation.objects.bulk_create(q_likes)
        print("Success.")

        n_q_dislikes = count // 4
        q_dislikes = [None] * n_q_dislikes
        print('Question dislikes generating...')
        for j in range(n_q_dislikes):
            print(j)
            profile_id = random.randint(prof_min_id, prof_max_id)
            question_id = random.randint(que_min_id, que_max_id)
            while (profile_id, question_id) in used_pairs:
                profile_id = random.randint(prof_min_id, prof_max_id)
                question_id = random.randint(que_min_id, que_max_id)
            used_pairs.append((profile_id, question_id))

            question = Question.objects.get(id=question_id)
            question.rating -= 1
            question.save()

            q_dislikes[j] = Reputation(reputation=-1, profile_id=profile_id, content_object=question)
        Reputation.objects.bulk_create(q_dislikes)
        print("Success.")

        ans_min_id = Answer.objects.order_by('id')[0].id
        ans_max_id = Answer.objects.order_by('-id')[0].id

        n_a_likes = count // 4
        a_likes = [None] * n_a_likes
        used_pairs = []
        print("Answer likes generating...")
        for j in range(n_a_likes):
            print(j)
            profile_id = random.randint(prof_min_id, prof_max_id)
            answer_id = random.randint(ans_min_id, ans_max_id)
            while (profile_id, answer_id) in used_pairs:
                profile_id = random.randint(prof_min_id, prof_max_id)
                answer_id = random.randint(ans_min_id, ans_max_id)
            used_pairs.append((profile_id, answer_id))

            answer = Answer.objects.get(id=answer_id)
            answer.rating += 1
            answer.save()

            a_likes[j] = Reputation(reputation=1, profile_id=profile_id, content_object=answer)
        Reputation.objects.bulk_create(a_likes)
        print("Success.")

        n_a_dislikes = count - n_a_likes * 3
        a_dislikes = [None] * n_a_dislikes
        print("Answer dislikes generating...")
        for j in range(n_a_dislikes):
            print(j)
            profile_id = random.randint(prof_min_id, prof_max_id)
            answer_id = random.randint(ans_min_id, ans_max_id)
            while (profile_id, answer_id) in used_pairs:
                profile_id = random.randint(prof_min_id, prof_max_id)
                answer_id = random.randint(ans_min_id, ans_max_id)
            used_pairs.append((profile_id, answer_id))

            answer = Answer.objects.get(id=answer_id)
            answer.rating -= 1
            answer.save()

            a_dislikes[j] = Reputation(reputation=-1, profile_id=profile_id, content_object=answer)
        Reputation.objects.bulk_create(a_dislikes)
        print("Success.")