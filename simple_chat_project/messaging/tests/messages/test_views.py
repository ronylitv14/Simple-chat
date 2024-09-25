import pytest
from django.urls import reverse
from rest_framework import status
from ...models import Message
from ...api.serializers import MessageSerializer


@pytest.fixture
def message(thread, default_user1):
    return Message.objects.create(thread=thread, sender=default_user1, text="Message 1")


@pytest.fixture
def unread_message(thread, default_user2):
    return Message.objects.create(thread=thread, sender=default_user2, text="Message 2")


@pytest.mark.django_db
class TestMessageEndpoints:

    def test_get_message_list(self, api_client, thread, message):
        """
        Ensure we can retrieve all messages for a thread.
        """
        url = reverse("messages-list")
        response = api_client.get(url, {"thread_id": thread.id})
        assert response.status_code == status.HTTP_200_OK

        messages_db = Message.objects.filter(thread=thread)
        serializer = MessageSerializer(messages_db, many=True)
        assert response.data["count"] == len(serializer.data)

    def test_create_message(self, api_client, thread, default_user1):
        """
        Ensure a message is created successfully.
        """
        url = reverse("messages-list")
        response = api_client.post(
            path=url,
            data={
                'thread': thread.id,
                'sender': default_user1.id,
                'text': 'New message body'
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        messages_db = Message.objects.filter(thread=thread)
        assert messages_db.count() == 1

    def test_mark_message_as_read(self, api_client, message):
        """
        Ensure a message can be marked as read.
        """
        url = reverse("messages-mark-as-read", kwargs={"pk": message.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK

        message.refresh_from_db()
        assert message.is_read is True

    def test_get_unread_messages_count(self, api_client, thread, unread_message):
        """
        Ensure the unread message count is accurate.
        """
        url = reverse("messages-unread")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['unread_count'] == 1
