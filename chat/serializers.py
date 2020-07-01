from rest_framework.serializers import(
	Serializer,
	SerializerMethodField,
    FileField,
    CharField,
    ModelSerializer,
	 )

from accounts.models import ViewingAndViewers
class UploadMediaSerializer(Serializer):
    video = FileField(allow_empty_file=True, error_messages={'required': 'video key is required'})
    audio = FileField(allow_empty_file=True, error_messages={'required': 'audio key is required'})
    thumb = FileField(allow_empty_file=True, error_messages={'required': 'thumb key is required'})
    image = FileField(allow_empty_file=True, error_messages={'required': 'image key is required'})


class ViewersListSerializer(ModelSerializer):
    id = SerializerMethodField()
    first_name = SerializerMethodField()
    last_name =SerializerMethodField()
    profile_image = SerializerMethodField()


    def get_id(self, instance):
        return instance.blog_by.id

    def get_first_name(self , instance):
        return instance.blog_by.first_name

    def get_last_name(self, instance):
        return instance.blog_by.last_name

    def get_profile_image(self, instance):
        if instance.blog_by.profile_image:
            return instance.blog_by.profile_image.url
        return None

    class Meta:
        model = ViewingAndViewers
        fields = ['id','first_name','last_name','profile_image']


class SendNotificationSerializer(Serializer):
    sendTo = CharField(error_messages={'required': 'sendTo key is required', 'blank':'sendTo is required'})
    title  = CharField(error_messages={'required': 'title key is required', 'blank':'title is required'})
    message = CharField(error_messages={'required': 'message key is required', 'blank':'message is required'})
    notificationType = CharField(error_messages={'required': 'notificationType key is required', 'blank':'notificationType is required'})
