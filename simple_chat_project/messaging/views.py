from datetime import datetime

from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import PermissionDenied

from .forms import RegisterForm
from .models import Thread, Message
from .api.serializers import (
    ThreadSerializer,
    MessageSerializer,
    MarkAsReadSerializer
)


# Basic home page
class HomePageView(TemplateView):
    template_name = "index.html"


class RegisterView(FormView):
    template_name = "register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


# API
class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Thread.objects.none()
        if not self.request.user.is_staff:
            return Thread.objects.filter(participants=self.request.user)
        if user_id := self.request.query_params.get("user_id"):
            return Thread.objects.filter(participants=user_id)
        return super().get_queryset()

    def destroy(self, request, *args, **kwargs):
        thread = self.get_object()
        if request.user.is_staff or thread.participants.filter(id=request.user.id).exists():
            thread.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied("You do not have permission to delete this thread.")


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        thread_id = self.request.query_params.get('thread_id')
        if thread_id:
            return Message.objects.filter(
                thread_id=thread_id,
                thread__participants=self.request.user)
        return Message.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.context['request'] = request
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        thread_id = serializer.data.get("thread_id")
        if thread_id:
            Thread.objects.filter(pk=thread_id).update(updated=datetime.now())

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        message = Message.objects.get(pk=pk)
        serializer = MarkAsReadSerializer(message, data={'is_read': True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'message marked as read'})

    @action(detail=False, methods=['get'])
    def unread(self, request):
        count = Message.objects.filter(
            thread__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()
        return Response({'unread_count': count})
