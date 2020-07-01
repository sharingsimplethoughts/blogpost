from django.db import models
from accounts.models import User

# Create your models here.
class MediaFile(models.Model):
    file = models.FileField(upload_to='chat_media/', blank=True, null=True, max_length=1000)
    thumb = models.FileField(upload_to='video_thumb/', blank=True, null=True, max_length=1000)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id + ": " + str(self.file)


class GroupMemberLists(models.Model):
    group_id = models.CharField(max_length=500)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_user')

    def __str__(self):
        return self.group_id+ ": " + str(self.user_id)