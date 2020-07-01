from accounts.models import User

from rest_framework.views import APIView
from rest_framework.response import Response

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from .models import MediaFile ,  GroupMemberLists
from blog.settings import BASE_URL
from .serializers import UploadMediaSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from accounts.models import ViewingAndViewers
from django.db.models import F
from django.db.models import Q
from .serializers import *
cred = credentials.Certificate("blog-app-firebase-adminsdk-q0n0c-1d0ee55d88.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://blog-app.firebaseio.com'
})

from common.common import send_multiple_notification_for_android,send_single_notification,get_error, send_multiple_notification, send_notification_by_url,send_notification_by_topic

def createNode(first_name, last_name, id, profile_image):
    firebase_admin.get_app()
    root = db.reference('Users')
    new_user = root.child('user_'+str(id)).set({
        'id':id,
        'name': first_name+' ' +last_name,
        'profile_image': profile_image
    })


def updateNode(first_name, last_name, id, profile_image):
    firebase_admin.get_app()
    root = db.reference('Users')
    new_user = root.child('user_'+str(id)).update({

        'name': first_name+' ' +last_name,
        'profile_image':profile_image
    })


def deleteNode(id):
    firebase_admin.get_app()
    root = db.reference('Users')
    new_user = root.child('user_'+str(id)).delete()


class UploadMedia(APIView):
    def post(self, request):
        data = request.FILES
        # serializer = UploadMediaSerializer(data=request.FILES)
        # if serializer.is_valid():
        images = data.getlist('image',[])
        video = data.get('video',None)
        thumb = data.get('thumb', None)
        audio = data.get('audio', None)
        doc = data.get('docs', None)
        video_url =''
        thumb_url = ''
        images_url =[]
        audio_url = ''
        docs_url = ''

        if images and not images==[]:
            for image in images:
                img_obj = MediaFile.objects.create(file=image)
                images_url.append({'image_url': BASE_URL+img_obj.file.url})


        elif video:
            if not thumb:
                return  Response({
                'message':'Thumbnail is required with video'
            },400)
            video_obj = MediaFile.objects.create(file=video, thumb=thumb)
            video_url = BASE_URL+video_obj.file.url
            thumb_url = BASE_URL+video_obj.thumb.url

        elif audio:
            audio_obj = MediaFile.objects.create(file=audio)
            audio_url = BASE_URL+audio_obj.file.url
        elif doc:
            docs_obj = MediaFile.objects.create(file=doc)
            docs_url = BASE_URL + docs_obj.file.url
        else:
            return Response({
                'message':'Please Provide at least one media file'
            },400)

        data ={
            'video':video_url,
            'audio':audio_url,
            'image':images_url,
            'thumb':thumb_url,
            'doc':docs_url
        }

        return Response({
            'data':data
        },200)

        # error_keys = list(serializer.errors.keys())
        # if error_keys:
        #     error_msg = serializer.errors[error_keys[0]]
        #     return Response({'message': error_msg[0]}, status=400)
        # return Response(serializer.errors, status=400)


class ViewersListAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self,request):
        user = request.user

        qs = user.viewers.all()
        data = ViewersListSerializer(qs, many=True).data
        return Response({
            'data': data,
        }, 200)


class SendNotification(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]
    def post(self, request):
        user = request.user
        data = request.data
        serializer = SendNotificationSerializer(data=data)
        if serializer.is_valid():
            user_id =data.get('sendTo')
            try:
                send_to_user = User.objects.get(id=user_id)
            except:
                return Response({
                    'message':'invalid user id'
                })
            profile_image =  user.profile_image
            device_type = send_to_user.device_type
            notificationType = data.get('notificationType')
            if profile_image:
                profile_image = profile_image.url
            else:
                profile_image = ''
            data = {
                'sendBy':user.id,
                'sendTo':send_to_user.id,
                'message':data.get('message'),
                'title':data.get('title'),
                'fullName':user.first_name + ' ' + user.last_name,
                'profilePic':profile_image,
                'call_status':'',
                'call_id':data.get('call_id'),
                'body':"blog",
                'notificationType':notificationType
            }
            # result = send_single_notification(send_to_user.device_token, device_type, data)
            result = send_notification_by_url(send_to_user.device_token,notificationType,device_type, data)
            if result.status_code == 200:
                return Response({
                'message':"sent successfully",
                    'result': 200,
                    'data': data
                 }, 200)
            else:
                return Response({
                    'message': "Somthing went wrong",
                     'result':result.status_code
                }, 500)

        return Response({'message':get_error(serializer) },400)


class SendNotificationByTopic(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        data = request.data
        topic = data.get('topic', None)
        if topic is None:
            return Response({
                'message': 'please provide topic'
            })
        response = send_notification_by_topic(topic, data)
        if response.status_code == 200:
            return Response({
                'message': "sent successfully",
                'result': 200,
                'data': data
            }, 200)
        else:
            return Response({
                'message': "Somthing went wrong",
                'result': response.status_code
            }, 500)

class SaveGroupMemberIds(APIView):
    # permission_classes = (IsAuthenticated,)
    # authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        data = dict(request.data)
        member_ids = data.get("member_ids", [])
        group_id = request.data.get("group_id", None)
        if not group_id:
            return Response({
                'message':"Please provide group id"
            }, 400)
        if not member_ids:
            return Response({
            'message': "Please provide member id"
            }, 400)
        if len(member_ids)==0:
            return Response({
                'message':"please provide at least one member id "
            })
        for id in member_ids:
            try:
                user = User.objects.get(id=id)
            except:
                return Response({
                    'message': "Invalid user id "+id
                })
            GroupMemberLists.objects.create(group_id=group_id, user_id = user)

        return Response({
            'message':"successfully saved"
        }, 200)


class SendMultipleNotification(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        data= request.data
        call_user_id = request.user.id
        group_id = request.data.get("group_id" , None)
        notificationType = request.data.get("notificationType", None)
        if not group_id:
            return  Response({
                "message":"please provide group id"
            }, 400)
        if not notificationType:
            return  Response({
                "message":"please provide notificationType"
            }, 400)


        # devices_id = GroupMemberLists.objects.filter(group_id=group_id).exclude(user_id=request.user).values_list('user_id__device_token', flat=True)
        # if not devices_id.exists():
        #     return Response({
        #         'message': "No user in this group or no user in this group"
        #     }, 400)
        # response = send_multiple_notification(devices_id, data)

        # on demand of android and ios developer( android required only data key and ios required notification key)

        devices_id = GroupMemberLists.objects.filter(group_id=group_id).exclude(user_id=request.user).values('user_id__device_token', 'user_id__device_type')
        if not devices_id.exists():
            return Response({
                'message': "No user in this group or no user in this group"
            }, 400)


        for devices_id in devices_id:
            response = send_notification_by_url(devices_id['user_id__device_token'],notificationType, devices_id['user_id__device_type'], data)
        if response.status_code == 200:
            return Response({
                'message': "sent successfully",
                'result': 200,
                'data': data
            }, 200)
        else:
            return Response({
                'message': "Somthing went wrong",
                'result': response.status_code
            }, 500)


        # android_devices_id = GroupMemberLists.objects.filter(group_id=group_id, user_id__device_type='1').exclude(user_id=request.user).values_list('user_id__device_token', flat=True)
        # ios_devices_id = GroupMemberLists.objects.filter(group_id=group_id, user_id__device_type='2').exclude(user_id=request.user).values_list('user_id__device_token', flat=True)
        #
        # if not android_devices_id.exists() and not ios_devices_id.exists():
        #     return Response({
        #         'message': "No user in this group"
        #     }, 400)
        # if ios_devices_id.exists():
        #     response = send_multiple_notification(list(ios_devices_id), data)
        #     if not response.status_code == 200:
        #         return Response({
        #             'message': "Somthing went wrong",
        #             'result': response.status_code
        #         }, 500)
        # if android_devices_id.exists():
        #     response = send_multiple_notification_for_android(list(android_devices_id), data)
        #     if response.status_code == 200:
        #         return Response({
        #             'message': "sent successfully",
        #             'result': 200,
        #             'data': data
        #         }, 200)
        #     else:
        #         return Response({
        #             'message': "Somthing went wrong",
        #         'result': response.status_code
        #     }, 500)




