import factory
from factory.django import DjangoModelFactory
from accounts.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    is_active = True
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    bio = factory.Faker('text', max_nb_chars=200)
    avatar = None