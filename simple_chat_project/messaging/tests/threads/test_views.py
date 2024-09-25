import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status

from ...api.serializers import ThreadSerializer
from ...models import Thread


@pytest.mark.django_db
class TestThreadEndpoints:

    def test_get_thread_list(self, api_client, thread, default_user1):
        """
        Ensure we can retrieve all threads for the authenticated user.
        """
        api_client.force_authenticate(user=default_user1)

        url = reverse("threads-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        threads_db = Thread.objects.filter(participants=default_user1)
        serializer = ThreadSerializer(threads_db, many=True)
        assert response.data["count"] == len(serializer.data)

    def test_create_thread(self, api_client, default_user1, default_user2):
        """
        Ensure a thread is created successfully.
        """
        url = reverse("threads-list")
        response = api_client.post(
            path=url,
            data={
                'participants': [default_user1.id, default_user2.id]
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        threads_db = Thread.objects.all()
        assert threads_db.count() == 1

    def test_get_thread(self, api_client, thread):
        """
        Ensure a specific thread is retrieved successfully.
        """
        url = reverse("threads-detail", kwargs={"pk": thread.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        serializer = ThreadSerializer(thread)
        assert response.data == serializer.data

    def test_delete_thread(self, api_client, thread):
        """
        Ensure a thread is successfully deleted.
        """
        url = reverse("threads-detail", kwargs={"pk": thread.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        with pytest.raises(ObjectDoesNotExist):
            Thread.objects.get(pk=thread.id)
