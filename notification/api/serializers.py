from rest_framework.serializers import(
     ModelSerializer,
     EmailField,
     CharField,
     SerializerMethodField,
     BooleanField,
     NullBooleanField,
     Serializer,
     ChoiceField,
     ImageField,
     FileField,
     ListField,
     DateField,
     TimeField,
     ValidationError
     )

from ..models import *
from common.common import CustomBooleanField
from blog.settings import BASE_URL



class NotificationSerializer(ModelSerializer):
    created = SerializerMethodField()

    def get_created(self, instance):
          return instance.get_date()

    class Meta:
        model = Notifications
        fields = [
             'id',
             'type',
             'message',
             'title',
             'image',
             'user',
             'post_id',
             'created'
        ]