from celery import shared_task
from django.template.loader import render_to_string
from django.core import mail
from accounts.models import User
from blog.settings import BASE_URL
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from accounts.api.tokens import account_activation_token
from chat.views import createNode, deleteNode, updateNode
from posts.models import *
from authy.api import AuthyApiClient

authy_api = AuthyApiClient('fgfghf')
from rest_framework_jwt.settings import api_settings
import random
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
from common.common import send_prize_notification, send_simple_notification_ios
from notification.models import Notifications

@shared_task(track_started=True)
def send_email_verify_mail(user_id):
    user_obj = User.objects.get(id=user_id)

    subject = 'Activate Your blog Account'
    to = user_obj.email
    plain_message = None
    from_email = 'blog <webmaster@localhost>'
    message_text = render_to_string('account_activation/account_activation_email.html', {
        'user': user_obj,
        'domain': BASE_URL,
        'uid': urlsafe_base64_encode(force_bytes(user_obj.pk)).decode(),
        'token': account_activation_token.make_token(user_obj),
    })
    mail.send_mail(subject, plain_message, from_email, [to], html_message=message_text)
    print('done')
    return 'success..!!'

@shared_task(track_started=True)
def send_phone_verify_otp(country_code, mobile_number):
    request = authy_api.phones.verification_start(mobile_number, country_code,
    									via='sms', locale='en')
    if request.content['success'] == True:
        return 'successfully send message'
    else:
        return 'faild to send message' + request.content['message']

@shared_task(track_started=True)
def create_user_node(first_name, last_name, id, profile_image):
    createNode(first_name, last_name ,id, profile_image)
    return 'successfully created user node'

@shared_task(track_started=True)
def update_user_node(first_name, last_name, id, profile_image):
    updateNode(first_name, last_name ,id, profile_image)
    return 'successfully updated user node'

@shared_task(track_started=True)
def delete_user_node(id):
    deleteNode(id)
    return 'successfully created user node'

@shared_task(track_started=True)
def select_winners(comp_id):
    print('start123')
    comp_post_obj = CompetitionPost.objects.get(post__id=comp_id)
    print(comp_post_obj.id)
    print(comp_post_obj)
    entered_user_list = CompetitionEnteredUsers.objects.filter(post__id=comp_id).values_list('entered_by', flat=True)
    no_of_winners = int(comp_post_obj.no_of_winners)
    print( entered_user_list)

    if len(entered_user_list) > no_of_winners:
        winners = random.sample(entered_user_list, no_of_winners)
    else:
        winners = entered_user_list
    print('start2')
    winner_obj = CompetitionWinners.objects.create(post=comp_post_obj.post)
    winner_obj.winners.add(*winners)

    android_user_qs = User.objects.filter(id__in =winners, device_type ='1')
    ios_user_qs = User.objects.filter(id__in =winners, device_type ='2')

    ## send user notification
    data = {
        'notificationType':'1',
        'post_id':comp_post_obj.id,
        'message': 'You won the competition',
        'title': 'Wow',
    }
    if android_user_qs.exists():
        res = send_prize_notification(list(android_user_qs.values_list('device_token', flat=True)),'1',data)
        print(res,'android')
    if ios_user_qs.exists():
        res = send_prize_notification(list(ios_user_qs.values_list('device_token', flat=True)), '2', data)
        print(res,'ios')

    if comp_post_obj.post.created_by.profile_image:
        image = comp_post_obj.post.created_by.profile_image.url
    else:
        image = ''

    all_users = (android_user_qs | ios_user_qs).distinct()

    # save in DB

    for user in all_users:
        Notifications.objects.create(type='1',message='You won the competition',title='Wow', image=image,
                                     post_id = comp_post_obj,user = user)

    print('end')
    return 'end'

@shared_task(track_started=True)
def send_action_notification(type, post_id, user_id):
    """
    1-prize winner
    2-Post like
    3-share
    4-comment
    5-like comment

    """

    user = User.objects.get(id=user_id)
    post_obj = Post.objects.get(id=post_id)


    if user.profile_image:
        image = user.profile_image.url
    else:
        image = ''

    if type==2:
        message = '{} {} liked your post.'.format(user.first_name,user.last_name)
    elif type==3:
        message = '{} {} shared your post.'.format(user.first_name, user.last_name)
    elif type==4:
        message = '{} {} commented on your post.'.format(user.first_name,user.last_name)
    else:
        message = '{} {} liked your comment.'.format(user.first_name, user.last_name)

    Notifications.objects.create(type=type, message=message, title='blog', image=image,
                                     post_id_actions = post_obj, user = post_obj.created_by)

    data = {
        'notificationType': type,
        'post_id': post_id,
        'message': message,
        'title': 'blog',
    }

    if user.device_type=='2':
        send_prize_notification([post_obj.created_by.device_token], post_obj.created_by.device_type, data)
    if user.device_type=='1':
        from pyfcm import FCMNotification
        fcm_server_key = 'fcm_server_key'
        push_service=FCMNotification(api_key=fcm_server_key)
        registration_id=post_obj.created_by.device_token
        message_title="blog App Notification"
        message_body=message
        result=push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
        print(result)

    return 'success'

@shared_task(track_started=True)
def send_simple_notification(user_id,message):
    user = User.objects.get(id=user_id)
    data = {
        'message': message,
        'title': 'blog',
    }
    if user.device_type=='2':
        send_prize_notification([user.device_token], user.device_type, data)
    if user.device_type=='1':
        from pyfcm import FCMNotification
        fcm_server_key = 'fcm_server_key'
        push_service=FCMNotification(api_key=fcm_server_key)
        registration_id=user.device_token
        message_title="blog App Notification"
        message_body=message
        result=push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
        print(result)


