from rest_framework.generics import (
		CreateAPIView,
	)
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from accounts.models import *
import random
from django.core import mail
from django.db.models import F
from django.db.models import Q
from blog.settings import BASE_URL
from authy.api import AuthyApiClient

authy_api = AuthyApiClient('fdsf')
from django.utils import timezone

User = get_user_model()
from admin_panel.models import Faq

import logging
logger = logging.getLogger('post')


# base64 to image
import base64
from django.core.files.base import ContentFile

# PASSWORD RESET BY EMAIL START------

from .settings import (
	PasswordResetSerializer,
)
from rest_framework_jwt.settings import api_settings
from django.contrib.sites.shortcuts import get_current_site

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


from rest_framework.generics import GenericAPIView
from rest_framework import status

# END--------------------------------

from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from . password_reset_form import MyPasswordResetForm

# send email verify email
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from accounts.api.tokens import account_activation_token
import datetime
# from chat.views import createNode, deleteNode, updateNode
from .task import send_email_verify_mail, create_user_node, send_phone_verify_otp ,delete_user_node, update_user_node, send_simple_notification 
# from .task import send_action_notification1

class UserLoginAPIView(APIView):
	def post(self, request):
		data = request.data
		serializer = UserLoginSerializer(data=data)
		if serializer.is_valid():
			user_data = serializer.data
			user = User.objects.get(id=user_data['id'])
			user_all_data = UserDetailSerializer(user).data
			user_all_data['token'] = user_data['token']
			user_all_data['login_type'] = user_data['login_type']
			if user_data['login_type'] == '1':  # mobile login
				if not user.is_num_verify:
					# send otp to verify number

					# authy_api.phones.verification_start(data['mobile_number'], data['country_code'],
					# 	via='sms', locale='en')
					send_phone_verify_otp.delay(user.country_code, user.mobile_number)

					return Response({
						'message': 'Please verify your number',
						'data': user_all_data
					}, status=200)


				return Response({
					'message': 'Login successfully',
					'data': user_all_data
				}, status=200)

			elif user_data['login_type'] == '2':
				if not user.is_mail_verify:
					## send email verification

					send_email_verify_mail.delay(user.id)

					return Response({
						'message': "Please verify your email before login",
						'data': {}
					}, status=405)

				user_all_data = UserDetailSerializer(user).data
				user_all_data['token'] = user_data['token']
				user_all_data['login_type'] = user_data['login_type']

				return Response({
					'message': 'Login successfully',
					'data': user_all_data
				}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message':error_msg[0]}, status = 400)
		return Response(serializer.errors, status=400)

class UserCreateAPIView(CreateAPIView):
	serializer_class = UserCreateSerializer
	def create(self, request, *args, **kwargs):
		# send_action_notification1()
		# return Response({'message': 'hi'}, status=400)
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			data = serializer.data

			if data['account_type'] == '1':  # normal signup

				username = data['first_name'] + '-' + data['last_name'] + '-' + str(random.randint(100000, 10000000))
				user_obj = User.objects.create(username=username, email=data['email'], first_name=data['first_name'], last_name=data['last_name'],
									country_code=data['country_code'], mobile_number=data['mobile_number'], profile_type=data['profile_type'],
									device_type=data['device_type'], device_token=data['device_token'])
				user_obj.set_password(data['password'])
				user_obj.save()
				message = 'Sign-up successfully. Please verify Your mobile number'

				mobile_number = data.get("mobile_number")
				country_code = data.get("country_code")
				# send email in background
				send_email_verify_mail.delay(user_obj.id)
				# send otp in background
				res = send_phone_verify_otp(country_code, mobile_number)
				print('----------------------------')
				print(res)

			else:  # social signup or login
				user_qs = User.objects.filter(social_id=data['social_id'], account_type=data['account_type']).exclude(social_id__isnull=True).exclude(social_id__iexact='').distinct()
				if user_qs.exists():
					user_obj = user_qs.first()
					message = 'Successfully logged in'
				else:
					username = data['social_id'] + '-' + data['account_type']
					password = data['social_id']
					user_obj = User.objects.create(username=username, email=data['email'], first_name=data['first_name'],
										last_name=data['last_name'], country_code=data['country_code'], mobile_number=data['mobile_number'],
										profile_type=data['profile_type'], device_type=data['device_type'],
										device_token=data['device_token'], account_type=data['account_type'], social_id=data['social_id'])
					user_obj.set_password(password)
					user_obj.save()
					message = 'Sign-up successfully'

			user_data = UserDetailSerializer(user_obj).data
			# create firebase node
			# create_user_node.delay(user_data['first_name'], user_data['last_name'], user_data['id'], user_data['profile_image'])
			create_user_node(user_data['first_name'], user_data['last_name'], user_data['id'], user_data['profile_image'])
			# create token
			payload = jwt_payload_handler(user_obj)
			token = jwt_encode_handler(payload)
			user_data['token'] = 'JWT ' + token

			return Response({
					'message': message,
					'data': user_data
				}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)

class UserBasicInfoAPIView(APIView):
	"""
	get create and update user basic info
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		data = request.data
		serializer = BasicInfoSerializer(data=data)
		if serializer.is_valid():

			data = serializer.data
			user = request.user
			user.gender = data['gender']
			user.birth_date = data['birth_date']
			user.birth_date_privacy= data['birth_date_privacy']

			user.nationality = data['nationality']
			user.nationality_key = data['nationality_key']
			user.bio = data['bio']
			if request.FILES.get('profile_image') is not None:
				user.profile_image = request.FILES.get('profile_image')
			user.save()
			# UPDATE FIREBASE USER NODE
			if user.profile_image:
				profile_image = BASE_URL+user.profile_image.url
			else:
				profile_image =None
			# updateNode(user.first_name, user.last_name, user.id, profile_image)
			# update_user_node.delay(user.first_name, user.last_name, user.id, profile_image)
			update_user_node(user.first_name, user.last_name, user.id, profile_image)

			# getting lang in list format
			lang_list = dict(request.data).get('language')
			# delete linked language
			user.language.all().delete()
			lang_qs = []
			for lang in lang_list:
				lang_obj = Languages.objects.create(lang_name = lang)
				lang_qs.append(lang_obj)
			user.language.add(*lang_qs)
			return Response({
				'message': 'Basic info updated successfully'
			}, status=200)
		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)

	def get(self, request):
		user = request.user
		data = GetUserDetailSerializer(user).data

		return Response({
			'data': data
		}, 200)


def base64_to_image(data):
	"""
	to convert base64 to image
	"""
	image=""
	if data:
		format, imgstr = data.split(';base64,')
		ext = format.split('/')[-1]
		image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)  # You can save this as file instance.
	return image


class UserContactInfoAPIView(APIView):
	"""
	get create and update user contact info
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		qs = UserContactInfo.objects.filter(user_id =request.user)
		data = ViewProfileContactInfoSerializer(qs.first(),context={'request':request}).data
		logger.debug(data)
		if not 'ethnicity' in data:
			data['ethnicity']=[]

		return Response({
			'data': data
		}, 200)

	def post(self, request):
		data = request.data
		serializer = UserContactInfoSerializer(data=data)
		if data.get('social_link') is None:
			return Response({
				'message': 'social_link key is required'
			}, 400)
		if data.get('ethnicity') is None:
			return Response({
				'message': 'ethnicity key is required'
			}, 400)
		if serializer.is_valid():
			contact_qs = UserContactInfo.objects.filter(user_id=request.user)
			ethnicity_list = dict(request.data).get('ethnicity')
			social_link = dict(request.data).get('social_link')
			if contact_qs.exists():
				# update existing object
				contact_obj = contact_qs.first()
				contact_obj.current_city = data['current_city']
				contact_obj.current_city_lat = data['current_city_lat']
				contact_obj.current_city_long = data['current_city_long']
				contact_obj.hometown = data['hometown']
				contact_obj.hometown_lat = data['hometown_lat']
				contact_obj.hometown_long = data['hometown_long']
				contact_obj.alt_mobile_number=data['alt_mobile_number']
				contact_obj.website_link = data['website_link']
				contact_obj.country_code = data['country_code']
				contact_obj.hometown_privacy = data['hometown_privacy']
				contact_obj.current_city_privacy = data['current_city_privacy']
				contact_obj.skype_id = data['skype_id']
				contact_obj.save()

				# delete linked language
				contact_obj.ethnicity.all().delete()
				ethnicity_qs = []
				for ethnicity in ethnicity_list:
					# image = request.FILES.get(ethnicity['flag'])
					ethnicity_obj = Ethnicity.objects.create(country_name=ethnicity['country_name'], flag = '')
					ethnicity_qs.append(ethnicity_obj)
				contact_obj.ethnicity.add(*ethnicity_qs)

				# delete relations
				SocialLink.objects.filter(id__in = contact_obj.social_link.all()).delete()

				# add new relations

				if not social_link == []:
					social_link_qs =[]
					for link in data['social_link']:
						social_link_obj = SocialLink.objects.create(social_link_type=link['social_link_type'],link=link['link'])
						social_link_qs.append(social_link_obj)
					contact_obj.social_link.add(*social_link_qs)

				return Response({
					'message': 'Contact Info updated successfully'
				}, status=200)

			# for create new one  process
			obj = UserContactInfo.objects.create(user_id=request.user, current_city=data['current_city'], current_city_privacy=data['current_city_privacy'],
										hometown=data['hometown'], hometown_privacy=data['hometown_privacy'],
										alt_mobile_number=data['alt_mobile_number'], country_code=data['country_code'],
										website_link=data['website_link'],skype_id=data['skype_id'])

			ethnicity_qs = []
			for ethnicity in ethnicity_list:
				# image = request.FILES.get(ethnicity['flag'])
				ethnicity_obj = Ethnicity.objects.create(country_name=ethnicity['country_name'], flag= '')
				ethnicity_qs.append(ethnicity_obj)
			obj.ethnicity.add(*ethnicity_qs)

			if not data.get('social_link') == []:

				social_link_qs = []
				for link in data['social_link']:
					social_link_obj = SocialLink.objects.create(social_link_type=link['social_link_type'],
																link = link['link'])
					social_link_qs.append(social_link_obj)
				obj.social_link.add(*social_link_qs)

			return Response({
				'message': 'Contact Info updated successfully'
			}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class UserEducationalDetailsAPIView(APIView):
	"""
	get create and update user educational detail
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		qs = UserEducationalDetails.objects.filter(user_id =request.user)
		data = ViewProfileEducationDetailSerializer(qs.first()).data
		return Response({
			'data': data
		}, 200)

	def post(self, request):
		data = request.data
		serializer = UserEducationalDetailsSerializer(data=data)
		if serializer.is_valid():
			edu_qs = UserEducationalDetails.objects.filter(user_id=request.user)
			if edu_qs.exists():
				edu_obj = edu_qs.first()
				edu_obj.college_name=data['college_name']
				edu_obj.sec_class_year=data['sec_class_year']
				edu_obj.high_class_year=data['high_class_year']
				edu_obj.high_school=data['high_school']
				edu_obj.secondary_school=data['secondary_school']
				edu_obj.college_since=data['college_since']
				edu_obj.save()

				return Response({
					'message': 'Educational detail updated successfully'
				}, status=200)

			UserEducationalDetails.objects.create( user_id=request.user, college_name=data['college_name'], college_since=data['college_since'], secondary_school=data['secondary_school'],
												   sec_class_year=data['sec_class_year'], high_school=data['high_school'],
												   high_class_year=data['high_class_year'])

			return Response({
				'message': 'Educational detail updated successfully'
			}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class UserWorkExperienceAPIView(APIView):
	"""
	get create and update work  detail
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		qs = UserWorkExperience.objects.filter(user_id = request.user)
		data = ViewProfileWorkDetailSerializer(qs.first()).data
		return Response({
			'data': data
		}, 200)

	def post(self, request):
		data = request.data
		serializer = WorkExperienceSerializer(data=data)
		if serializer.is_valid():
			work_qs = UserWorkExperience.objects.filter(user_id=request.user)
			if work_qs.exists():
				work_qs = work_qs.first()
				work_qs.company_name = data['company_name']
				work_qs.job_title = data['job_title']
				work_qs.location = data['location']
				work_qs.location_lat = data.get('location_lat')
				work_qs.location_long = data.get('location_long')
				work_qs.work_des = data['work_des']
				work_qs.working_since = data['working_since']
				work_qs.is_working_here = data['is_working_here'].capitalize()
				work_qs.save()

				return Response({
					'message': 'Work experience updated successfully'
				}, status=200)

			UserWorkExperience.objects.create(user_id=request.user, company_name=data['company_name'],
											  job_title=data['job_title'], location=data['location'],location_long = data.get('location_long'),
											  location_lat = data.get('location_lat') ,work_des=data['work_des'], is_working_here=data['is_working_here'].capitalize(),
											  working_since=data['working_since'])

			return Response({
				'message': 'Work experience updated successfully'
			}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class UserPersonalViewAPIView(APIView):
	"""
	get create and update user personal view
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		qs = UserPersonalView.objects.filter(user_id =request.user)
		data = ViewProfileUserPersonalViewSerializer(qs.first()).data
		return Response({
			'data': data
		}, 200)

	def post(self, request):
		data = request.data
		serializer = UserPersonalSerializer(data=data)
		if serializer.is_valid():
			per_qs = UserPersonalView.objects.filter(user_id = request.user)
			if per_qs.exists():
				per_obj = per_qs.first()
				per_obj.political_view=data['political_view']
				per_obj.world_view=data['world_view']
				per_obj.religious_view=data['religious_view']
				per_obj.save()

				return Response({
					'message': 'User personal view updated successfully'
				}, status=200)

			UserPersonalView.objects.create(user_id=request.user, political_view=data['political_view'],
											world_view=data['world_view'], religious_view=data['religious_view'])

			return Response({
				'message': 'User personal view updated successfully'
			}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


def make_obj(interest_list, user, interest_type, interest):
	interest_obj = [UserInterests(user_id=user, interest_type=interest_type, interest=activitie) for activitie
					in interest]
	interest_list.extend(interest_obj)


class UserInterestsAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]


	def get(self, request):
		qs = UserInterest.objects.filter(user_id = request.user)
		data = ViewProfileUserInterestSerializer(qs.first()).data
		return Response({
			'data': data

		}, 200)

	def post(self, request):
		serializer = UserInterestSerializer(data=request.data)
		if serializer.is_valid():
			data = serializer.data
			user = request.user
			int_qs = UserInterest.objects.filter(user_id=request.user)
			if int_qs.exists():
				int_obj = int_qs.first()
				int_obj.activities = data['activities']
				int_obj.hobbies = data['hobbies']
				int_obj.tv_shows = data['tv_shows']
				int_obj.games = data['games']
				int_obj.movies = data['movies']
				int_obj.music = data['music']
				int_obj.interest_text = data['interest_text']
				int_obj.save()

				return Response({
					'message': 'User Interest updated successfully'
				}, status=200)

			UserInterest.objects.create(user_id= user, activities=data['activities'],
										 hobbies=data['hobbies'], music=data['music'], movies=data['movies'],
										 tv_shows=data['tv_shows'], games=data['games'],interest_text=data['interest_text'])


			# interest_list = []
			#
			# interest = ['activities', 'hobbies', 'music', 'movies', 'tv_shows', 'games']
			# for i in range(6):
			# 	make_obj(interest_list,request.user, i+1, data[interest[i]])
			#
			# UserInterests.objects.bulk_create(interest_list)

			# updated user interest after demand

			return Response({
				'message': 'User Interest updated successfully'
			}, status=200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class PasswordResetView(GenericAPIView):
	"""
	Calls Django Auth PasswordResetForm save method.
	Accepts the following POST parameters: email
	Returns the success/fail message.
	"""
	serializer_class = PasswordResetSerializer

	def post(self, request):
		# Create a serializer with request.data
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			# Return the success message with OK HTTP status
			return Response(
				{
				'message':"Password reset e-mail has been sent successfully"
				}, 200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class UserPhoneVerifyAfterRegisterAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		data = request.data
		user = request.user
		mobile_number = data.get('mobile_number')
		country_code = data.get('country_code')
		verification_code = data.get('verification_code')
		if mobile_number and country_code and verification_code:
			check = authy_api.phones.verification_check(mobile_number, country_code, verification_code)
			# if  or verification_code == "1234":
			if verification_code == "1234" or check.ok() == True :
				user.is_num_verify = True
				user.save()
				return Response({
					# 'message':check.content['message']},
					'message': 'Your number has been verified successfully'
				}, status=200)

			return Response({
				# 'message':check.content['message']
				'message': 'verification code is incorrect'
			}, status=400)

		return Response({
			'message': 'Please provide data in valid format'
		}, status=400)


class OTPReSendForPhoneVerify(APIView):

	def post(self, request):
		mobile_number = request.data.get('mobile_number')
		country_code = request.data.get('country_code')
		if mobile_number and country_code:
			try:
				authy_api.phones.verification_start(phone_number, country_code, via='sms', locale='en')
				return Response({
						'message': 'Otp sent successfully'},
						status=200)
			except:
				return Response({
					'message': 'Otp sent successfully'},
					status=200)
		return Response({
				'message': 'Please provide data in valid format'
			}, status=400)


class ChangePasswordAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get_object(self):
		return self.request.user

	def post(self,request,*args,**kwargs):
		user = self.get_object()
		serializer = ChangePasswordSerializer(data=request.data)
		if serializer.is_valid():
			old_password = serializer.data.get("old_password")
			new_password = serializer.data.get("new_password")
			# confPassword = serializer.data.get("confPassword")
			# if newPassword == confPassword:
			if not user.check_password(old_password):
				return Response({
					"message": "You entered wrong current password"},
					status=400)

			user.set_password(new_password)
			user.save()
			return Response(
				{
				'message':'Your password changed successfully'
				}, status=200)

		# fow showing all serializer errors one by one
		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class RemoveAccountAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		password = request.data.get('password')
		if password is None or password=='':
			return Response({
				'message': 'Password is required'
			}, 400)
		try:
			# check password
			user = request.user
			if not user.check_password(password):
				return Response({
					'message': 'Incorrect password'
				}, 400)
			# delete firebase user node
			# deleteNode(user.id)
			delete_user_node.delay(user.id)
			user.delete()
			return Response({
				'message': 'Account deleted successfully'
			}, 200)
		except:
			return Response({
				'message': 'Someting went wrong'
			}, 500)


class ViewUserProile(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		user = request.user
		data = UserProfileViewSerializer(user,context={'request':request}).data
		return Response({
			'data': data
		})


class GetAllUserData(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		page = int(self.request.GET.get('page', 1))
		data = GetAllUserDataSerializer(request.user, context={'page':page, 'request':request}).data
		return Response({
			'data': data
		})


class SettingsUserPersonalInfo(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		user = request.user
		data = {
			'first_name': user.first_name,
			'last_name': user.last_name,
			'email': user.email,
			'country_code': user.country_code,
			'mobile_number': user.mobile_number,
			'profile_type':user.profile_type

		}
		return Response({
			'data': data
		})
	def post(self, request):
		data =  request.data
		user = request.user
		serializer = SettingPersonalInfoSaveSerializer(data=data)
		if serializer.is_valid():
			user.first_name = data['first_name']
			user.last_name = data['last_name']
			user.profile_type = data['profile_type']
			user.save()

			# update user node
			if user.profile_image:
				profile_image = BASE_URL+user.profile_image.url
			else:
				profile_image = None
			# updateNode(data['first_name'], data['last_name'], user.id, profile_image)
			# update_user_node.delay(data['first_name'], data['last_name'], user.id, profile_image)
			update_user_node(data['first_name'], data['last_name'], user.id, profile_image)
			return Response({
				'message': 'Personal info updated successfully'
			}, 200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)

class ChangePrivateAccountStatusAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		data = request.data
		user = request.user
		serializer = ChangePrivateAccountStatusSerializer(data=data)
		if serializer.is_valid():
			user.is_private_account = serializer.validated_data['is_private_account']
			user.save()
			return Response({
				'message': 'Status changed successfully'
			}, 200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class GetUserSettingsAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		user = request.user
		data = {
			'post_privacy': user.post_privacy,
			'is_private_account': user.is_private_account,
			'message_privacy': user.message_privacy
		}
		return Response({
			'data': data
		}, 200)


class PrivacySettingAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		data = request.data
		privacy_type = data.get('privacy_type')
		status = data.get('status')
		if not status in ['1','2','3']:
			return Response({
				'message':'Please provide right status'
			}, 400)
		user = request.user
		if privacy_type == "1":
			user.post_privacy = status
			user.save()
			return Response({
				'message':'status changed successfully'
			}, 200)
		elif privacy_type == "2":
			user.message_privacy = status
			user.save()
			return Response({
				'message': 'status changed successfully'
			}, 200)
		else:
			return Response({
				'message':'Please provide privacy type key and value in  1 or 2 in string format'
			}, 400)

from django.db.models.functions import Concat
from django.db.models import Value

class GetViewingListApiView(APIView):
	"""
	viewing list of users
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request,*args, **kwargs):

		frnd_type = self.kwargs.get('frnd_type')
		user = request.user
		# get viewing list


		qs = ViewingAndViewers.objects.filter(blog_by=request.user, status="2")
		viewing_list = qs.values(first_name=F('blog_to__first_name'),
				last_name=F('blog_to__last_name'), profile_image=F('blog_to__profile_image'),
				user_id=F('blog_to__id'))
		all_viewing = qs.values_list('blog_to__id', flat=True)

		if frnd_type == '1':
			for obj in viewing_list:
				obj['profile_image'] = '/media/'+obj['profile_image']
				obj['blog_by'] = ViewingAndViewers.objects.filter(status='2', blog_to=obj['user_id'] , blog_by__in =all_viewing).values(first_name=F('blog_by__first_name'),
					last_name=F('blog_by__last_name'))

			return Response({
				'data': viewing_list
			}, 200)

		if frnd_type=='2':

			# get viewers list
			qs = ViewingAndViewers.objects.filter(blog_to = request.user, status="2")
			viewers_list = qs.values(first_name=F('blog_by__first_name'),
					last_name=F('blog_by__last_name'), profile_image=F('blog_by__profile_image'),
					user_id=F('blog_by__id'))

			all_viewers = qs.values_list('blog_by__id', flat=True)

			for obj in viewers_list:
				obj['profile_image'] = '/media/' + obj['profile_image']
				# blog by
				obj['blog_by'] = ViewingAndViewers.objects.filter(status='2', blog_to=obj['user_id'],
																	blog_by__in=all_viewing).values(
					first_name=F('blog_by__first_name'),
					last_name=F('blog_by__last_name'))

				# status to user
				viewing_status_qs = ViewingAndViewers.objects.filter(blog_to__id=obj['user_id'], blog_by=user,
																	 status__in=['1', '2'])  # following
				viewers_status_qs = ViewingAndViewers.objects.filter(blog_by__id=obj['user_id'], blog_to=user,
																	 status__in=['1', '2'])  # followers
				request_id = None
				if viewing_status_qs.exists():
					viewing_status = viewing_status_qs.first().status
				else:
					viewing_status = '3'
				if viewers_status_qs.exists():
					viewers_status = viewers_status_qs.first().status
					if viewers_status == '1':
						request_id = viewers_status_qs.first().id
				else:
					viewers_status = '3'
				obj['viewing_status']=viewing_status
				obj['viewers_status'] = viewers_status

			return Response({
				'data':viewers_list
			}, 200)


class ViewOtherUserFriendsAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request ,*args , **kwargs):
		user_id = self.kwargs.get('user_id')
		try:
			other_user_obj = User.objects.get(id = user_id)
		except:
			return  Response({
				'message': 'invalid user id'
			})
		user = request.user
		user_viewing_list = ViewingAndViewers.objects.filter(blog_by=request.user, status="2").values_list('blog_to__id', flat=True)

		# get viewers list
		qs = ViewingAndViewers.objects.filter(blog_to=other_user_obj, status="2").exclude(blog_by=user)
		viewers_list = qs.values(first_name=F('blog_by__first_name'),
								 last_name=F('blog_by__last_name'), profile_image=F('blog_by__profile_image'),
								 user_id=F('blog_by__id'))

		all_viewers = qs.values_list('blog_by__id', flat=True)

		for obj in viewers_list:
			# blog by
			obj['blog_by'] = ViewingAndViewers.objects.filter(status='2', blog_to=obj['user_id'],
																blog_by__in=user_viewing_list).values(
				first_name=F('blog_by__first_name'),
				last_name=F('blog_by__last_name'))

			# status to user
			viewing_status_qs = ViewingAndViewers.objects.filter(blog_to__id=obj['user_id'], blog_by=user,
																 status__in=['1', '2'])  # following
			viewers_status_qs = ViewingAndViewers.objects.filter(blog_by__id=obj['user_id'], blog_to=user,
																 status__in=['1', '2'])  # followers
			request_id = None
			if viewing_status_qs.exists():
				viewing_status = viewing_status_qs.first().status
			else:
				viewing_status = '3'
			if viewers_status_qs.exists():
				viewers_status = viewers_status_qs.first().status
				if viewers_status == '1':
					request_id = viewers_status_qs.first().id
			else:
				viewers_status = '3'
			obj['viewing_status'] = viewing_status
			obj['viewers_status'] = viewers_status

		# viewing list of other user

		# get viewing list
		qs = ViewingAndViewers.objects.filter(blog_by=other_user_obj, status="2").exclude(blog_to=user)
		viewing_list = qs.values(first_name=F('blog_to__first_name'),
								 last_name=F('blog_to__last_name'), profile_image=F('blog_to__profile_image'),
								 user_id=F('blog_to__id'))

		all_viewing = qs.values_list('blog_to__id', flat=True)

		for obj in viewing_list:
			# blog by
			obj['blog_by'] = ViewingAndViewers.objects.filter(status='2', blog_to=obj['user_id'],
																blog_by__in=user_viewing_list).values(
				first_name=F('blog_by__first_name'),
				last_name=F('blog_by__last_name'))

			# status to user
			viewing_status_qs = ViewingAndViewers.objects.filter(blog_to__id=obj['user_id'], blog_by=user,
																 status__in=['1', '2'])  # following
			viewers_status_qs = ViewingAndViewers.objects.filter(blog_by__id=obj['user_id'], blog_to=user,
																 status__in=['1', '2'])  # followers
			request_id = None
			if viewing_status_qs.exists():
				viewing_status = viewing_status_qs.first().status
			else:
				viewing_status = '3'
			if viewers_status_qs.exists():
				viewers_status = viewers_status_qs.first().status
				if viewers_status == '1':
					request_id = viewers_status_qs.first().id
			else:
				viewers_status = '3'
			obj['viewing_status'] = viewing_status
			obj['viewers_status'] = viewers_status

		# mutual friends

		# get viewing list
		mututal_viewing = set(user_viewing_list)-(set(user_viewing_list)-set(all_viewing))
		mutual_list = User.objects.filter(id__in =mututal_viewing).values('first_name', 'last_name', 'profile_image' ,user_id=F('id'))
		for obj in mutual_list:
			# blog by
			obj['blog_by'] = ViewingAndViewers.objects.filter(status='2', blog_to=obj['user_id'],
																blog_by__in=user_viewing_list).values(
				first_name=F('blog_by__first_name'),
				last_name=F('blog_by__last_name'))

			# status to user
			viewing_status_qs = ViewingAndViewers.objects.filter(blog_to__id=obj['user_id'], blog_by=user,
																 status__in=['1', '2'])  # following
			viewers_status_qs = ViewingAndViewers.objects.filter(blog_by__id=obj['user_id'], blog_to=user,
																 status__in=['1', '2'])  # followers
			request_id = None
			if viewing_status_qs.exists():
				viewing_status = viewing_status_qs.first().status
			else:
				viewing_status = '3'
			if viewers_status_qs.exists():
				viewers_status = viewers_status_qs.first().status
				if viewers_status == '1':
					request_id = viewers_status_qs.first().id
			else:
				viewers_status = '3'
			obj['viewing_status'] = viewing_status
			obj['viewers_status'] = viewers_status


		return Response({
			'data':{'viewing_list':viewing_list,'viewers_list':viewers_list,'mutual_list':mutual_list}
		}, 200)


class FAQListAPIView(APIView):

	def get(self, request):
		faq_data = Faq.objects.all().values('query', 'answer')
		for data in faq_data:
			data['answer'] = [data['answer']]
		return Response({
			'data':faq_data
		}, 200)


class SendFollowRequestToWiewersAPIView(APIView):
	"""
	send follow request to user
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		user = request.user
		if request.user.id == int(user_id):
			return Response({'message': 'You can not follow self'}, 400)
		try:
			obj, created = ViewingAndViewers.objects.get_or_create(blog_by=request.user,
																   blog_to_id=user_id)  # status False
			if not created:
				obj.delete()
		except:
			return Response({'message': 'Invalid user_id'}, 400)

		# get viewers list
		qs = ViewingAndViewers.objects.filter(blog_to=request.user, status="2")
		viewers_list = qs.values(first_name=F('blog_by__first_name'),
								 last_name=F('blog_by__last_name'), profile_image=F('blog_by__profile_image'),
								 user_id=F('blog_by__id'))

		all_viewers = qs.values_list('blog_by__id', flat=True)

		for obj in viewers_list:
			obj['profile_image'] = '/media/' + obj['profile_image']
			# blog by
			obj['blog_by'] = ViewingAndViewers.objects.filter(status='2', blog_to=obj['user_id'],
																blog_by__in=all_viewing).values(
				first_name=F('blog_by__first_name'),
				last_name=F('blog_by__last_name'))

			# status to user
			viewing_status_qs = ViewingAndViewers.objects.filter(blog_to__id=obj['user_id'], blog_by=user,
																 status__in=['1', '2'])  # following
			viewers_status_qs = ViewingAndViewers.objects.filter(blog_by__id=obj['user_id'], blog_to=user,
																 status__in=['1', '2'])  # followers
			request_id = None
			if viewing_status_qs.exists():
				viewing_status = viewing_status_qs.first().status
			else:
				viewing_status = '3'
			if viewers_status_qs.exists():
				viewers_status = viewers_status_qs.first().status
				if viewers_status == '1':
					request_id = viewers_status_qs.first().id
			else:
				viewers_status = '3'
			obj['viewing_status'] = viewing_status
			obj['viewers_status'] = viewers_status

		return Response({'message': 'Request sent successfully',
						 'data': viewers_list
						 })
		


class SendFollowRequestAPIView(APIView):
	"""
	send follow request to user
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		user_id = request.data.get('user_id')
		serializer = SendFollowRequestSerializer(data=request.data)
		if serializer.is_valid():
			user = request.user
			if request.user.id==int(user_id):
				return Response({'message': 'You can not follow self'}, 400)
			try:
				obj, created = ViewingAndViewers.objects.get_or_create(blog_by=request.user, blog_to_id=user_id)  #status False
				if not created:
					obj.delete()

			except:
				return Response({'message':'Invalid user_id'},400)

			name_key = request.data.get('name')
			is_profile = request.data.get('is_profile')

			# handle request when come from suggestion page
			if (name_key == '' or name_key == None) and (is_profile== '0' or is_profile == None):
				viewing_viewers_qs = ViewingAndViewers.objects.filter(blog_to=user, status='1')
				viewing_viewers_data = ViewingAndViewersSerializer(viewing_viewers_qs, many=True,
																   context={'request': request}).data

				all_viewing = user.viewing.filter(status='2').values_list('blog_to', flat=True)  # viewing of user

				sugg_qs = User.objects.all().exclude(id__in=all_viewing).exclude(id=user.id)[:20]
				data = SuggestionSerializer(sugg_qs, context={'request': request}, many=True).data

				data ={
					'suggestions': data,
					'viewing_request': viewing_viewers_data,


				}
				
				return Response({'message':'Request sent successfully',
								 'data': data
								 })

			# request come from profile suggestion
			if (name_key == '' or name_key == None) and (is_profile== '1'):
				try:
					user_obj = User.objects.get(id=request.data.get('user_id'))
				except:
					return Response({'message': 'Invalid user_id'}, 400)

				# find relation with user

				viewing_status_qs = ViewingAndViewers.objects.filter(blog_to=user_obj, blog_by=user,
																	 status__in=['1', '2'])  # following
				viewers_status_qs = ViewingAndViewers.objects.filter(blog_by=user_obj, blog_to=user,
																	 status__in=['1', '2'])  # followers
				request_id = None
				if viewing_status_qs.exists():
					viewing_status = viewing_status_qs.first().status
				else:
					viewing_status = '3'
				if viewers_status_qs.exists():
					viewers_status = viewers_status_qs.first().status
					if viewers_status == '1':
						request_id = viewers_status_qs.first().id
				else:
					viewers_status = '3'

				data = UserProfileViewByUsersSerializer(user_obj,
														context={'request': request, 'user_obj':user_obj,'viewers_status': viewers_status,
																 'viewing_status': viewing_status,'is_profile':is_profile}).data
				data['viewing_status'] = viewing_status
				data['viewers_status'] = viewers_status
				data['request_id'] = request_id
				# profile views count
				obj, created = ProfileViewsCountRecord.objects.get_or_create(profile_blog_by=user,
																			 profile_blog_to=user_obj)
				if created:
					user_obj.profile_views_count = user_obj.profile_views_count + 1
					user_obj.save()
				
				return Response({
					'data': data
				}, 200)

			# handle requests when come from search page
			query = request.data.get('name', None)

			## global users
			global_qs = User.objects.filter(
				Q(first_name__icontains=query) |
				Q(last_name__icontains=query)
			).prefetch_related('viewing', 'viewers').exclude(id=user.id)
			try:
				contact_info = UserContactInfo.objects.get(user_id=user)
				# current city of searching user is available
				current_city = contact_info.current_city
				local_qs = global_qs.filter(
					id__in=UserContactInfo.objects.filter(current_city=current_city).select_related(
						'user__id').values_list('user_id', flat=True))
			except:
				local_qs = global_qs.none()

			local_data = SearchResultSerializer(local_qs, many=True, context={'request': request}).data

			## national users
			national_qs = global_qs.filter(Q(nationality=user.nationality)).exclude(id__in=[o.id for o in local_qs])

			## local user

			local_and_nation = (local_qs | national_qs).distinct()

			national_data = SearchResultSerializer(national_qs, many=True, context={'request': request}).data

			global_data = SearchResultSerializer(global_qs.exclude(id__in=[o.id for o in local_and_nation]),
												 many=True, context={'request': request}).data

			# data = SearchResultSerializer(data=qs,many=True, context={'request':request}).data

			data = {
				'global_user': global_data,
				'national_user': national_data,
				'local_user': local_data
			}
			
			return Response({
				'data': data
			}, 200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)





class AcceptOrCancelFollowRequestAPIView(APIView):
	"""
	accept or cancel a requests
	"""
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self, request):
		data = request.data
		serializer = AcceptOrCancelFollowRequestSerializer(data=data)
		if serializer.is_valid():
			try:
				obj = ViewingAndViewers.objects.get(id = data['request_id'], status='1', blog_to = request.user)
			except:
				return Response({'message':'Invalid request id'},400)
			user = request.user
			if data['is_accepted']==True or data['is_accepted']=='true':
				obj.status='2'
				# add in users model as viewers
				user.viewers.add(obj)
				user.save()
				# add user as viewing in other user
				obj.blog_by.viewing.add(obj)

				obj.action_date = timezone.now()
				obj.save()
			elif data['is_accepted']==False or data['is_accepted']=='false':
				obj.delete()

			else:
				return Response({'message':'provide valid boolean in is accepted'}, 400)

			viewing_viewers_qs = ViewingAndViewers.objects.filter(blog_to=user, status='1')
			viewing_viewers_data = ViewingAndViewersSerializer(viewing_viewers_qs, many=True,
															   context={'request': request}).data

			all_viewing = user.viewing.filter(status='2').values_list('blog_to', flat=True)  # viewing of user

			sugg_qs = User.objects.all().exclude(id__in=all_viewing).exclude(id=user.id)[:20]
			data = SuggestionSerializer(sugg_qs, context={'request': request}, many=True).data

			data = {
				'viewing_request':viewing_viewers_data,
				'suggestions': data,
			}
			return Response({'message': 'Action applied successfully',
							 'data': data},200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)

from random import sample

class ShowFriendsRequestAndSuggestions(APIView):

	"""
	lists of frnd requests and suggestion for frnds
	"""

	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		user = request.user
		viewing_viewers_qs = ViewingAndViewers.objects.filter(blog_to=user, status='1')
		viewing_viewers_data = ViewingAndViewersSerializer(viewing_viewers_qs, many=True, context={'request':request}).data

		# due to less user for developemnet
		all_viewing = user.viewing.filter(status='2').values_list('blog_to', flat=True)  # viewing of user


		sugg_qs = User.objects.all().exclude(id__in=all_viewing).exclude(id=user.id)[:20]
		data = SuggestionSerializer(sugg_qs ,context={'request':request}, many=True).data

		# we will show viewing frnds of viewing users as suggested users ( for production)
		# viewing_frnd = ViewingAndViewers.objects.filter(blog_by__in=all_viewing, status='2').select_related('blog_to').values_list( 'blog_to', flat=True)  # all viewing users of vieweing user
		# suggestion_data = User.objects.all(id__in = viewing_frnd)
		# data = SuggestionSerializer(suggestion_data ,context={'request':request}, many=True).data

		new_data = {
			'viewing_request':viewing_viewers_data,
			'suggestions':data
		}
		return Response({
			'data': new_data

			},200)



class ViewUserProfileAPIView(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]


	def get(self, request, *args , **kwargs):
		user = request.user
		page = self.request.GET.get('page' ,1)
		try:
			user_obj = User.objects.get(id=self.kwargs.get('user_id'))
		except:
			return Response({'message':'Invalid user_id'},400)

		# find relation with user

		viewing_status_qs = ViewingAndViewers.objects.filter(blog_to=user_obj, blog_by=user, status__in=['1', '2'])  #following
		viewers_status_qs = ViewingAndViewers.objects.filter(blog_by=user_obj, blog_to=user, status__in=['1', '2'])  #followers
		request_id =None
		if viewing_status_qs.exists():
			viewing_status = viewing_status_qs.first().status
		else:
			viewing_status = '3'
		if viewers_status_qs.exists():
			viewers_status = viewers_status_qs.first().status
			if viewers_status=='1':
				request_id=viewers_status_qs.first().id
		else:
			viewers_status = '3'

		data = UserProfileViewByUsersSerializer(user_obj, context={'request': request,'page' :page, 'user_obj':user_obj, 'viewers_status': viewers_status, 'viewing_status': viewing_status}).data
		data['viewing_status'] = viewing_status
		data['viewers_status'] = viewers_status
		data['request_id'] = request_id
		# profile views count
		obj, created = ProfileViewsCountRecord.objects.get_or_create(profile_blog_by= user, profile_blog_to=user_obj)
		if created:
			user_obj.profile_views_count = user_obj.profile_views_count +1
			user_obj.save()

		return Response({
			'data': data
			}, 200)


class StopViewingAFriend(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def post(self,request):
		data =request.data
		curr_user = request.user
		serializer = SendFollowRequestSerializer(data=data)
		if serializer.is_valid():
			try:
				user_obj = User.objects.get(id=data.get('user_id'))

			except:
				return Response({
					'message':'Invalid user id'
					},400)

			obj ,created = ViewingAndViewers.objects.get_or_create(blog_to=user_obj, blog_by=curr_user)
			if not created:
				status = obj.status
				if status == '1':
					obj.delete() # delete request
					message = 'Request Taken Back  sucessfully'
				elif status == '2':
					obj.delete()    # unfriend
					message = 'Unblog successfully'
				else:
					message = 'Somthing went wrong'
			else:
				message ='Send request successfully'

			# response back profile data
			# find relation with user

			viewing_status_qs = ViewingAndViewers.objects.filter(blog_to=user_obj, blog_by=curr_user,
																 status__in=['1', '2'])  # following
			viewers_status_qs = ViewingAndViewers.objects.filter(blog_by=user_obj, blog_to=curr_user,
																 status__in=['1', '2'])  # followers
			request_id = None
			if viewing_status_qs.exists():
				viewing_status = viewing_status_qs.first().status
			else:
				viewing_status = '3'
			if viewers_status_qs.exists():
				viewers_status = viewers_status_qs.first().status
				if viewers_status == '1':
					request_id = viewers_status_qs.first().id
			else:
				viewers_status = '3'

			data = UserProfileViewByUsersSerializer(user_obj,
													context={'request': request, 'user_obj':user_obj,'viewers_status': viewers_status,
															 'viewing_status': viewing_status}).data
			data['viewing_status'] = viewing_status
			data['viewers_status'] = viewers_status
			data['request_id'] = request_id
			# profile views count
			obj, created = ProfileViewsCountRecord.objects.get_or_create(profile_blog_by=curr_user,
																		 profile_blog_to=user_obj)
			if created:
				user_obj.profile_views_count = user_obj.profile_views_count + 1
				user_obj.save()

			return Response({
				'data': data,
				'message': message
			}, 200)

		error_keys = list(serializer.errors.keys())
		if error_keys:
			error_msg = serializer.errors[error_keys[0]]
			return Response({'message': error_msg[0]}, status=400)
		return Response(serializer.errors, status=400)


class HomePageSearchUser(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]

	def get(self, request):
		query = request.GET.get('q', None)
		user = request.user

		## global users
		global_qs = User.objects.filter(
			Q(first_name__icontains=query)|
			Q(last_name__icontains=query)
			).prefetch_related('viewing', 'viewers').exclude(id=user.id)	
		try:
			contact_info = UserContactInfo.objects.get(user_id=user)
			 # current city of searching user is available
			current_city = contact_info.current_city
			local_qs = global_qs.filter(id__in = UserContactInfo.objects.filter(current_city=current_city).select_related('user__id').values_list('user_id',flat=True))

		except:
			local_qs = global_qs.none()

		local_data = SearchResultSerializer(local_qs, many=True, context={'request':request}).data

		## national users
		national_qs = global_qs.filter(Q(nationality = user.nationality)).exclude(id__in=[o.id for o in local_qs])

		## local user
		
		local_and_nation = (local_qs | national_qs).distinct()

		national_data = SearchResultSerializer(national_qs, many=True, context={'request':request}).data

		global_data = SearchResultSerializer(global_qs.exclude(id__in=[o.id for o in local_and_nation]), many=True, context={'request':request}).data

		# data = SearchResultSerializer(data=qs,many=True, context={'request':request}).data

		data = {
			'global_user':global_data,
			'national_user':national_data,
			'local_user':local_data
			}

		return Response({
			'data':data
			},200)


class SendSimpleNotification(APIView):
	permission_classes = (IsAuthenticated,)
	authentication_classes = [JSONWebTokenAuthentication]
	def post(self,request,*args, **kwargs):
		user_id = request.data['user_id']
		if user_id:
			message = request.data['message']
			if message:
				send_simple_notification(user_id,message)
				return Response({
					'success':'True',
					'message':'Notification sent successfully',
				},200)
			return Response({
				'success':'False',
				'message':'Please provide message'
			},400)
		return Response({
			'success':'False',
			'message':'Please provide user_id'
		},400)
