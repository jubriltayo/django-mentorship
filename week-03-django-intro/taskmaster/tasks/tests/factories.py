import factory
from factory.django import DjangoModelFactory
from tasks.models import Task, Category, Tag, Priority, Status


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Category {n}')
    description = factory.Faker('text', max_nb_chars=200)
    color = factory.Faker('hex_color')


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: f'tag-{n}')


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph')
    priority = Priority.MEDIUM
    status = Status.PENDING
    category = factory.SubFactory(CategoryFactory)
    owner = factory.SubFactory('accounts.tests.factories.UserFactory')

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)