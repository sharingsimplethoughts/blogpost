
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny,IsAuthenticated
from .serializers import *
from admin_panel.models import *
from posts.models import Post
from notification.models import Notifications
from authy.api import AuthyApiClient
authy_api = AuthyApiClient('fhfg')
from notification.api.serializers import NotificationSerializer

User = get_user_model()


class UserBlockAPIView(APIView):
    def post(self,request,*args,**kwargs):
        user_id = self.kwargs['user_id']

        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({
                'message': 'No user to block'},
                status=400)

        user.is_active = False
        user.save()

        return Response({

            'message': 'Blocked successfully'},
            status=200)


class UserUnblockAPIView(APIView):
    def post(self,request,*args,**kwargs):
        user_id = self.kwargs['user_id']
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({
                'message': 'No user to unblock'},
                status=400)
        user.is_active = True
        user.save()
        return Response({
            'message': 'Unblocked successfully'},
            status=200)


class UserDeleteAPIView(APIView):
    def post(self,request,*args,**kwargs):
        user_id = self.kwargs['user_id']
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response({
                'message': 'No user to delete'},
                status=400)
        user.delete()
        return Response({

            'message': 'deleted successfully'},
            status=200)


class FAQDeleteAPIView(APIView):

    def delete(self, request, *args, **kwargs):

        try:
            Faq.objects.get(id=self.kwargs.get('faq_id')).delete()
        except:
            return Response({

                'message': 'Somthing went wrong. Please try after some time'
            }, status=500)

        return Response({

            'message': 'Deleted Successfully'
        }, status=200)


class BlockUnblockPostAPIView(APIView):
    def post(self, request, *args, **kwargs):
        post_id = self.kwargs['post_id']
        try:
            post = Post.objects.get(id=post_id)
        except:
            return Response({
                'message': 'Invalid post id'},
                status=400)
        curr_status = post.is_active
        if curr_status:
            post.is_active = False
            status= 'Blocked'
        else:
            post.is_active = True
            status = 'Unblocked'

        post.save()
        return Response({
            'message': status+' successfully'},
            status=200)


class NotificationDeleteAPIView(APIView):
    def post(self,request,*args,**kwargs):
        id = self.kwargs['id']
        try:
            notif = Notifications.objects.get(id=id)
        except:
            return Response({
                'message': 'No notification to delete'},
                status=400)
        notif.delete()
        return Response({
            'message': 'deleted successfully'},
            status=200)


class AdminHomeHeaderView(APIView):
    def get(self, request):
        user = request.user
        print(user)
        notification = Notifications.objects.filter(user=user)
        data = NotificationSerializer(notification,many=True).data

        return Response({
            'notification':data,

            },
        status=200)


