from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from common.common import get_error, StandardResultsSetPagination
from django.db.models import F
from django.core.paginator import Paginator
import logging
logger = logging.getLogger('post')
from dateutil.relativedelta import relativedelta
from datetime import  timedelta


class NotificationListAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self,request):
        qs = Notifications.objects.filter(user = request.user).order_by('-created')
        data = NotificationSerializer(qs,many=True).data

        return Response({
            'data':data
        }, 200)
