from rest_framework.fields import empty
from rest_framework.serializers import(
	 Serializer,
     BooleanField,
	 )
from rest_framework import  pagination
from pyfcm import FCMNotification
import json
import requests
fcm_server_key = 'fcm_server_key'


def send_single_notification(device_id, device_type, data):
    # send on single device
    push_service = FCMNotification(api_key = fcm_server_key)

    registration_id = device_id
    if device_type=="1":
        result = push_service.notify_single_device(registration_id=registration_id,
                                               data_message =data)
    else:
        result = push_service.notify_single_device(registration_id=registration_id,
                                                   message_body="this is your message", data_message = data)
    return result

def send_notification_by_topic(topic, data):
    headers = {"Content-type": "application/json",
               "Authorization": "key="+fcm_server_key}
    url = "https://fcm.googleapis.com/fcm/send"
    data = {
        "to": "/topics/"+topic,
        "priority": "high",
        "data": data,
        "notification": data,

    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r

def send_multiple_notification(ids, data):
    headers = {"Content-type": "application/json",
               "Authorization": "key="+fcm_server_key}
    url = "https://fcm.googleapis.com/fcm/send"
    data = {
        "registration_ids": ids,
        "priority": "high",
        "content_available": True,
        "data": data,
        "notification": data,

    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r

def send_multiple_notification_for_android(ids, data):
    headers = {"Content-type": "application/json",
               "Authorization": "key="+fcm_server_key}
    url = "https://fcm.googleapis.com/fcm/send"
    data = {
        "registration_ids": ids,
        "priority": "high",
        "data": data,

    }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r


def send_notification_by_url(device_id, notificationType, device_type, data):
    headers = {"Content-type": "application/json",
               "Authorization": "key="+fcm_server_key}
    url = "https://fcm.googleapis.com/fcm/send"
    if device_type=='1': # for android
        data = {
            "to": device_id,
            "content_available": True,
            "priority": "high",
            "data":data
        }
    else:
        if notificationType =="VIDEO_CALL_REJECT" or notificationType =="AUDIO_CALL_REJECT":
            data = {
                "to": device_id,
                "content_available": True,
                "priority": "high",
                "notification": data,
            }
        else:
            data = {
                "to": device_id,
                "notification": data,
                "priority": "high",
                "data": data
            }

    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r


def send_prize_notification(ids, device_type, data):
    print('-----------hi------------------')
    headers = {"Content-Type": "application/json",
               "Authorization": "key="+fcm_server_key}
    url = "https://fcm.googleapis.com/fcm/send"
    if device_type=='1': # for android
        data = {
            "registration_ids": ids,
            "content_available": True,
            "priority": "high",
            "data":data
        }
    else:
        data = {
            "registration_ids": ids,
            "content_available": True,
            "notification": data,
            "priority": "high",
        }

    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r



def send_simple_notification_ios(ids, device_type, data):
    headers = {"Content-Type": "application/json",
               "Authorization": "key="+fcm_server_key}
    url = "https://fcm.googleapis.com/fcm/send"
    if device_type=='1': # for android
        data = {
            "registration_ids": ids,
            "content_available": True,
            "priority": "high",
            "data":data
        }
    else:
        data = {
            "registration_ids": ids,
            "content_available": True,
            "notification": data,
            "priority": "high",
        }

    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r


def send_multiple_devices_notification(device_ids):
    # Send to multiple devices by passing a list of ids.
    push_service = FCMNotification(api_key = fcm_server_key)
    registration_ids = device_ids
    message_title = "multi check"
    message_body = "Fcm multiple device is working"
    result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title,
                                                  message_body=message_body)
    print(result)


def get_error(serializer):
    error_keys = list(serializer.errors.keys())
    if error_keys:
        error_msg = serializer.errors[error_keys[0]]
        return error_msg[0]
    return serializer.errors

def get_error(serializer):
    error_keys = list(serializer.errors.keys())
    if error_keys:
        error_msg = serializer.errors[error_keys[0]]
        return error_msg[0]
    return serializer.errors

class CustomBooleanField(BooleanField):
    def get_value(self, dictionary):
        return dictionary.get(self.field_name, empty)

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


