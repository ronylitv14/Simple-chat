from django.contrib import admin
from .models import Message, Thread


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_participants', 'created', 'updated')
    search_fields = ('participants__username',)

    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])

    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'thread', 'created', 'is_read')
    list_filter = ('is_read', 'created')
    search_fields = ('sender__username', 'text')
