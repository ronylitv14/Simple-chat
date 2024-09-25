import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from ..models import Thread

DEFAULT_USERNAME = "default_username"
DEFAULT_PASSWORD = "Default_password"


@pytest.fixture
def default_user1():
    user_model = get_user_model()
    return user_model.objects.create_user(
        username=f"{DEFAULT_USERNAME}_1",
        password=DEFAULT_PASSWORD)


@pytest.fixture
def default_user2():
    user_model = get_user_model()
    return user_model.objects.create_user(
        username=f"{DEFAULT_USERNAME}_2",
        password=DEFAULT_PASSWORD)


@pytest.fixture
def api_client(default_user1):
    client = APIClient()
    client.force_authenticate(default_user1)
    return client


@pytest.fixture
def thread(default_user1, default_user2):
    thread = Thread.objects.create()
    thread.participants.set([default_user1, default_user2])
    return thread
