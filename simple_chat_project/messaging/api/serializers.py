from rest_framework import serializers
from django.contrib.auth.models import User

from ..models import Thread, Message


class ThreadSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all()
    )

    class Meta:
        model = Thread
        fields = ['participants', 'created', 'updated']

    def validate(self, attrs):
        participants = set(attrs.get("participants", []))
        request = self.context.get("request")
        user = request.user

        if not participants:
            raise serializers.ValidationError("There should be at least 1 participant.")

        participants.add(user)

        if len(participants) > 2:
            raise serializers.ValidationError("A thread must have exactly 2 unique participants.")

        attrs["participants"] = list(participants)
        return attrs

    def create(self, validated_data):
        participants = validated_data.pop('participants')
        participants = set(participants)

        existing_threads = Thread.objects.filter(participants__in=participants).distinct()
        for thread in existing_threads:
            if participants == set(thread.participants.all()):
                return thread
        thread = Thread.objects.create()
        thread.participants.set(participants)
        return thread


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.id')

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'thread', 'created', 'is_read']
        read_only_fields = ['created', 'is_read']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        message = Message.objects.create(**validated_data)
        return message


class MarkAsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['is_read']
