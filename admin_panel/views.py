from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
import datetime
# Create your views here.
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.models import *
from .forms import *
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login ,logout
from django.utils.decorators import method_decorator

from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from accounts.api.password_reset_form import MyPasswordResetForm
from accounts.models import *
from .models import *
from django.db.models import Sum
from posts.models import *
from notification.models import *
from django.contrib.auth import update_session_auth_hash
from django.db.models.functions import TruncMonth
from django.db.models import Count
from datetime import date

import csv
from django.http import HttpResponse
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractYear



class AdminLoginView(View):
	def get(self, request):
		form = LoginForm
		if request.user.is_authenticated:
			return HttpResponseRedirect('/admin/panel/home/')

		return render(request, 'admin_panel/accounts/login.html', {'form': form})

	def post(self, request):
		form = LoginForm(request.POST or None)
		if form.is_valid():
			user = User.objects.get(email=request.POST['email'],account_type="1", is_staff=True, is_superuser=True,)
			login(request, user)
			return HttpResponseRedirect('/admin/panel/home')

		return render(request, 'admin_panel/accounts/login.html', {'form': form})


class LogoutView(View):

	def get(self,request):
		logout(request)
		return HttpResponseRedirect('/admin/panel/login/')


class ResetPasswordView(auth_views.PasswordResetView):
	 form_class = MyPasswordResetForm


class ChangePasswordView(View):

	def get(self, request):
		form = ChangePasswordForm(user=request.user)
		return render(request, 'admin_panel/accounts/change_password.html', {'form': form})

	def post(self, request):
		user = request.user
		print(request.POST)
		form = ChangePasswordForm(request.POST or None, user=request.user)

		if form.is_valid():
			password = form.cleaned_data['password']
			user.set_password(password)
			user.save()
			update_session_auth_hash(request, form.user)
			# messages.success(request, 'Your password have been changed successfully. Please login again to access account')
			return HttpResponseRedirect('/admin/panel/login/')
		return render(request, 'admin_panel/accounts/change_password.html', {'form': form})

import itertools
class AdminHomeView(View):

	def get(self, request):
		user = request.user
		notification = Notifications.objects.filter(user= user)
		number_of_notification = len(notification)
		all_user = User.objects.all().count()
		all_posts = Post.objects.all().count()
		days_count = timezone.now() - datetime.timedelta(days=7)
		recently_joined_users = User.objects.filter(date_joined__gt=days_count).count()

		# Graph data
		month = timezone.now() - datetime.timedelta(days=30)
		posts_by_months = Post.objects.filter(
					created__range=(month, timezone.now())
				).values('created').order_by('created')
		grouped = itertools.groupby(posts_by_months, lambda d: d.get('created').strftime('%b %d'))
		posts = dict([(day, len(list(this_day))) for day, this_day in grouped])

		context = {
			'notification': notification,
			'number_of_notification':number_of_notification,
			'all_user':all_user,
			'all_posts':all_posts,
			'recently_joined_users':recently_joined_users,
			'total_download':0,
			'posts_by_months_keys':list(posts.keys()),
			'posts_by_months_values': list(posts.values())
		}
		return render(request, 'admin_panel/home.html', context)


class AdminProfileView(View):

	def get(self, request):

		form = AdminProfileEditForm
		user =request.user
		context = {

			'form': form,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'email': user.email,
			'mobile_number': user.mobile_number,
			'profile_image': user.profile_image,
			'cover_image': user.cover_image,
			'country_code': user.country_code
		}

		return render(request, 'admin_panel/accounts/admin_profile.html', context)


class AdminProfileEditView(View):
	def get(self, request):
		form = AdminProfileEditForm
		user = request.user
		context = {

			'form': form,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'email': user.email,
			'mobile_number': user.mobile_number,
			'profile_image': user.profile_image,
			'cover_image': user.cover_image,
			'country_code': user.country_code
		}

		return render(request, 'admin_panel/accounts/admin_profile_change.html', context)

	def post(self, request):
		data = request.POST
		user = request.user
		form = AdminProfileEditForm(request.POST or None, user=request.user)
		if form.is_valid():


			profile_image = request.FILES.get('profile_image')
			cover_image = request.FILES.get('cover_image')

			user.email = form.cleaned_data['email']
			user.first_name = form.cleaned_data['first_name']
			user.last_name = form.cleaned_data['last_name']
			user.mobile_number = form.cleaned_data['mobile_number']

			if profile_image is not None:
				user.profile_image = profile_image
			if cover_image is not None:
				user.cover_image = cover_image

			user.save()
			return HttpResponseRedirect('/admin/panel/admin_profile/')

		context = {

			'form': form,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'email': user.email,
			'mobile_number': user.mobile_number,
			'profile_image': user.profile_image,
			'cover_image': user.cover_image,
			'country_code': user.country_code
		}
		return render(request, 'admin_panel/accounts/admin_profile_change.html', context)


class UserListView(View):
	def get(self, request):
		users = User.objects.filter(is_staff=False).order_by('-date_joined')
		context = {

		'users':users,
		'sort_by': "default"

		}
		return render(request, 'admin_panel/account_management/user_list.html', context)


class UserdetailView(View):
	def get(self, request, *args, **kwargs):

		profile_id = self.kwargs['profile_id']
		user  = User.objects.prefetch_related('language').get(pk=profile_id)
		personal_view = UserPersonalView.objects.filter(user_id=user)
		education = UserEducationalDetails.objects.filter(user_id=user)
		contact_info = UserContactInfo.objects.filter(user_id=user).prefetch_related('social_link','ethnicity')
		work = UserWorkExperience.objects.filter(user_id=user)
		interest = UserInterest.objects.filter(user_id=user)
		context = {

		'userdata':user,
		'personal_view':personal_view,
		'education':education,
		'contact_info':contact_info,
		'work':work,
		'interest':interest

		}

		return render(request, 'admin_panel/account_management/userprofile.html', context)


class UserDateFilterView(View):
	def get(self, request):
		print(request.GET)

		start_date = datetime.datetime.strptime(request.GET.get('startdate'), '%m/%d/%Y').strftime('%Y-%m-%d')

		end_date = datetime.datetime.strptime(request.GET.get('enddate'), '%m/%d/%Y').strftime('%Y-%m-%d')

		filterdata = User.objects.filter(date_joined__range=(start_date, end_date), is_staff=False)
		context = {'users': filterdata, 'startdate' : request.GET.get('startdate'), 'enddate':request.GET.get('enddate'),'sort_by': 'dafault'}
		return render(request, 'admin_panel/account_management/user_list.html', context)


class NotificationDateFilterView(View):
	def get(self, request):
		print(request.GET)

		start_date = datetime.datetime.strptime(request.GET.get('startdate'), '%m/%d/%Y').strftime('%Y-%m-%d')

		end_date = datetime.datetime.strptime(request.GET.get('enddate'), '%m/%d/%Y').strftime('%Y-%m-%d')

		filterdata = Notifications.objects.filter(created__range=(start_date, end_date))
		context = {'notification_list': filterdata, 'startdate' : request.GET.get('startdate'), 'enddate':request.GET.get('enddate'),'sort_by': 'dafault'}

		return render(request , 'admin_panel/notification_management/notification_list.html', context)


class ReportsDateFilterView(View):
	def get(self, request):
		print(request.GET)

		start_date = datetime.datetime.strptime(request.GET.get('startdate'), '%m/%d/%Y').strftime('%Y-%m-%d')

		end_date = datetime.datetime.strptime(request.GET.get('enddate'), '%m/%d/%Y').strftime('%Y-%m-%d')

		filterdata = ReportAPost.objects.filter(created__range=(start_date, end_date))
		context = {'reports': filterdata, 'startdate' : request.GET.get('startdate'), 'enddate':request.GET.get('enddate'),'sort_by': 'dafault'}

		return render(request , 'admin_panel/report_management/reports_list.html', context)


class UserSortView(View):
	def post(self, request):

		data = request.POST['sort_by']

		if data=="default":
			return HttpResponseRedirect('/admin/panel/account_management/')

		filterdata = User.objects.filter(is_staff=False).order_by(data)

		context = {'users': filterdata,
				   'sort_by': data
				   }
		return render(request, 'admin_panel/account_management/user_list.html', context)

	def get(self, request):
		return HttpResponseRedirect('/admin/panel/account_management/')


class TermsAboutContactView(View):

	def get(self, request, *args, **kwargs):

		obj = ContactAboutTerms.objects.all().values('terms', 'id').first()

		if obj:
			terms = obj['terms']
			id = obj['id']
		else:
			terms = ''
			id = None

		context = {
			'terms': terms,
			'id': id
		}
		return render(request, 'admin_panel/settings_management/terms.html', context)

	def post(self, request, *args, **kwargs):

		data = request.POST
		print(data)
		form = ContactAboutTermsForm(data or None)
		if form.is_valid():
			if data['id'] == 'None':

				ContactAboutTerms.objects.create(
												 terms=form.cleaned_data['terms'],
												 )
				messages.success(request, 'Created successfully')

			else:
				obj = ContactAboutTerms.objects.get(id=int(data['id']))
				obj.terms = form.cleaned_data['terms']
				obj.save()
				messages.success(request, 'Updated successfully')

			return HttpResponseRedirect('/admin/panel/terms_and_condition/')

		context = {
			'form': form,
			'terms': data['terms'],
			'id': data.get('id'),

		}
		return render(request, 'admin_panel/settings_management/terms.html', context)


class CreateAboutUsView(View):

	def get(self, request, *args, **kwargs):

		obj = ContactAboutTerms.objects.all().values('about_us', 'id').first()

		if obj:
			about_us = obj['about_us']
			id = obj['id']
		else:
			about_us = ''
			id = None

		context = {
			'about_us': about_us,
			'id': id
		}
		return render(request, 'admin_panel/settings_management/about_us.html', context)

	def post(self, request, *args, **kwargs):

		data = request.POST
		print(data)
		form = ContactAboutTermsForm(data or None)
		if form.is_valid():
			if data['id'] == 'None':

				ContactAboutTerms.objects.create(about_us=form.cleaned_data['about_us'],
												)
				messages.success(request, 'Created successfully')

			else:
				obj = ContactAboutTerms.objects.get(id=int(data['id']))
				obj.about_us = form.cleaned_data['about_us']
				obj.save()
				messages.success(request, 'Updated successfully')

			return HttpResponseRedirect('/admin/panel/about_us/')

		context = {
			'form': form,
			'about_us': data['about_us'],
			'id': data.get('id'),
		}
		return render(request, 'admin_panel/settings_management/about_us.html', context)


class FAQView(View):

	def get(self, request, *args, **kwargs):
		faq_qs = Faq.objects.all()
		context = {
			'faqs': faq_qs
		}
		return render(request, 'admin_panel/settings_management/faq.html', context)

	def post(self, request, *args, **kwargs):
		data = request.POST
		form = FaqForm(request.POST or None)
		if form.is_valid():
			if data['id'] == 'None' or data['id'] == '':

				Faq.objects.create(query=form.cleaned_data['query'],
								   answer=form.cleaned_data['answer'])
				messages.success(request, 'Created successfully')

			else:
				obj = Faq.objects.get(id=int(data['id']))
				obj.query = form.cleaned_data['query']
				obj.answer = form.cleaned_data['answer']
				obj.save()
				messages.success(request, 'Updated successfully')

			return HttpResponseRedirect('/admin/panel/faq/')

		context = {
			'form': form,
			'about_us': data['query'],
			'terms': data['answer'],
			'id': data.get('id'),

		}

		return render(request, 'admin_panel/settings_management/faq.html', context)


class TMCView(View):
	def get(self, request):
		tmc = ContactAboutTerms.objects.all().values('terms').first()
		context = {'data':tmc}
		return render(request , 'app_web_pages/tmc.html', context)


class AboutUsView(View):
	def get(self, request):
		about_us = ContactAboutTerms.objects.all().first()
		context = {'data': about_us}
		return render(request , 'app_web_pages/about_us.html', context)


class UsersPostListView(View):
	def get(self, request):

		users = User.objects.all().order_by('-last_post_created')
		context = {'users':users,
				   'sort_by': "default"
					}
		return render(request , 'admin_panel/post_management/user_list_last_post.html', context)

	def post(self, request, *args, **kwargs):
		data = request.POST
		startdate = data.get("startdate")
		enddate = data.get("enddate")
		sort_by = data.get('sort_by')

		if sort_by=="default":
			users = User.objects.all().order_by('-last_post_created')
		else:
			users = User.objects.all().order_by(sort_by,'-last_post_created')

		if startdate and enddate:
			start_date = datetime.datetime.strptime(startdate, '%m/%d/%Y').strftime('%Y-%m-%d')
			end_date = datetime.datetime.strptime(enddate, '%m/%d/%Y').strftime('%Y-%m-%d')+ ' 23:59:59'

			users = users.filter(last_post_created__range= (start_date, end_date))


		context = {'users': users, 'startdate': startdate, 'enddate':enddate,'sort_by':sort_by}
		return render(request , 'admin_panel/post_management/user_list_last_post.html', context)



class UsersAllPostListView(View):
	def get(self, request, *args ,**kwargs):
		user_id = self.kwargs.get('user_id')
		posts = Post.objects.filter(created_by__id = user_id).order_by('-created')
		context = {'posts': posts,
				   'sort_by':"-created",
				   'user_id':user_id,
				   'sort_by_type':"0"
				   }
		return render(request, 'admin_panel/post_management/all_post.html', context)

	def post(self, request, *args, **kwargs):
		data = request.POST
		startdate = data.get("startdate")
		enddate = data.get("enddate")
		sort_by = data.get("sort_by")
		sort_by_type = data.get("sort_by_type")
		user_id = self.kwargs.get('user_id')

		if sort_by_type =="0":
			posts = Post.objects.filter(created_by__id=user_id).order_by(sort_by)
		else:
			posts = Post.objects.filter(created_by__id=user_id, post_type = sort_by_type).order_by(sort_by)

		if startdate and enddate:
			start_date = datetime.datetime.strptime(startdate, '%m/%d/%Y').strftime('%Y-%m-%d')
			end_date = datetime.datetime.strptime(enddate, '%m/%d/%Y').strftime('%Y-%m-%d')+ ' 23:59:59'
			posts = posts.filter(created__range=(start_date, end_date))

		context = {'posts': posts,'user_id':user_id,'startdate': startdate, 'enddate':enddate, 'sort_by':sort_by,'sort_by_type':sort_by_type}

		return render(request, 'admin_panel/post_management/all_post.html', context)


class UserAllPostSortView(View):
	def post(self, request,*args, **kwargs):
		data = request.POST['sort_by']
		print(data)
		user_id = self.kwargs.get('user_id')
		posts = Post.objects.filter(created_by__id = user_id).order_by(data)
		context = {'posts': posts,
				   'sort_by': data,
				   'user_id':user_id
				   }
		return render(request , 'admin_panel/post_management/all_post.html', context)

	# def get(self, request):
	# 	user_id = self.kwargs.get('user_id')
	# 	return HttpResponseRedirect('/admin/panel/user_posts/'+user_id)


from collections import  Counter
class ViewPostDetailView(View):
	def get(self, request, *args, **kwargs):
		post_id = self.kwargs.get('post_id')
		post = Post.objects.get(id = post_id)
		media = PostMediaFiles.objects.filter(post_id=post_id)
		context = {'post': post ,'medias':media}

		if post.post_type=='1':
			return render(request, 'admin_panel/post_management/text_post.html', context)

		elif post.post_type=='2':
			return render(request, 'admin_panel/post_management/image_post.html', context)

		elif post.post_type=='3':
			return render(request, 'admin_panel/post_management/video_post.html', context)

		elif post.post_type=='4':
			return render(request, 'admin_panel/post_management/audio_post.html', context)

		elif post.post_type=='5':
			poll_post = PollPost.objects.get(post=post)
			options = PollOptions.objects.filter(post=post)
			votes = VoteAPoll.objects.filter(post=post).values_list('poll_option', flat=True)
			votes_count = Counter(votes)
			for option in options:
				if votes_count.get(option.id, None):
					option.pecentage_vote = (votes_count[option.id] / votes.count()) * 100
				else:
					option.pecentage_vote = 0
			context['options'] = options
			context['poll_post'] =poll_post

			return render(request, 'admin_panel/post_management/poll_post.html', context)

		elif post.post_type =='6':
			comp = CompetitionPost.objects.get(post=post)
			prize_images = CompetitionPrizeImages.objects.filter(post=post)

			context['comp'] = comp
			context['prize_images'] = prize_images
			context['blog_by'] = CompetitionblogByUsers.objects.filter(post=post).count()
			context['entered_by'] = CompetitionEnteredUsers.objects.filter(post=post).count()

			return render(request, 'admin_panel/post_management/competition.html', context)
		else:
			return render(request, 'admin_panel/post_management/no_post.html', context)


class UserPostDateFilterView(View):
	def get(self, request):
		print(request.GET)

		start_date = datetime.datetime.strptime(request.GET.get('startdate'), '%m/%d/%Y').strftime('%Y-%m-%d')

		end_date = datetime.datetime.strptime(request.GET.get('enddate'), '%m/%d/%Y').strftime('%Y-%m-%d')+' 23:59:59'

		users = User.objects.filter(last_post_created__range=(start_date, end_date)).order_by('-last_post_created')
		context = {'users': users, 'startdate': request.GET.get('startdate'), 'enddate':request.GET.get('enddate'),'sort_by':"default"}
		return render(request , 'admin_panel/post_management/user_list_last_post.html', context)


class UserPostSortView(View):
	def post(self, request):
		data = request.POST['sort_by']
		if data=="default":
			return HttpResponseRedirect('/admin/panel/post_management/sort')
		users = User.objects.all().order_by(data,'-last_post_created')
		context = {'users': users,
				   'sort_by': data
				   }
		return render(request , 'admin_panel/post_management/user_list_last_post.html', context)

	def get(self, request):
		return HttpResponseRedirect('/admin/panel/post_management')


class UserAllPostSortView(View):
	def post(self, request,*args, **kwargs):
		data = request.POST['sort_by_type']
		user_id = self.kwargs.get('user_id')
		posts = Post.objects.filter(created_by__id = user_id, post_type = data)
		context = {'posts': posts,
				   'sort_by_type': data,
				   'user_id':user_id
				   }
		return render(request , 'admin_panel/post_management/all_post.html', context)


class NotificationView(View):
	def get(self, request,*args, **kwargs):
		users = User.objects.all()
		context = {'users': users}
		return render(request , 'admin_panel/notification_management/notification.html', context)

	def post(self, request):
		users = User.objects.all()
		if request.user.profile_image:
			profile_image = request.user.profile_image.url
		else:
			profile_image =''
		if request.method == "POST":
			data = request.POST
			title = request.POST.get('title')
			message = request.POST.get('message')
			alluser = request.POST.get('selectIsAllUser')

			if alluser == 'True':
				for user in users:
					selectedUsers = users.values_list('id',flat=True)
			else:
				stripeddata = request.POST.get('selectdUserArr')
				selectedUsers = ''
				if stripeddata:
					selectedUsers = stripeddata.split(",")

			if not title:
				messages.error(request, 'Please Enter title')
			if not message:
				messages.error(request, 'Please Enter Description text')
			if not selectedUsers and selectedUsers == '':
				messages.error(request, 'Please select atleast one user')
			else:
				for user in selectedUsers:
					if data:
						Notifications.objects.create(type=2, message=message, title=title, user_id=user , image=profile_image)
						messages.success(request, 'Notification Sent successfully')
					else:
						messages.error(request, 'Something is Wrong')

					return HttpResponseRedirect('/admin/panel/notification/')

			context = {'data': data, 'users':users}
		return render(request, "admin_panel/notification_management/notification.html", context)


class NotificationListView(View):
	def get(self, request,*args, **kwargs):
		notification_list = Notifications.objects.all()
		context = {'notification_list': notification_list}

		return render(request, 'admin_panel/notification_management/notification_list.html', context)


class ReportsListView(View):
	def get(self, request, *args, **kwargs):
		reports = ReportAPost.objects.all()

		context = {'reports': reports}
		return render(request, 'admin_panel/report_management/reports_list.html', context)


class ReportsGenerationView(View):

	def get(self, request):
		startdate = request.GET.get("startdate",'')
		enddate = request.GET.get("enddate",'')
		sort_by = request.GET.get("sort_by")


		if sort_by:
			start_date = timezone.now()
			if sort_by=='0':
				user_count = User.objects.all().count()

			elif sort_by=='1':# today
				user_count = User.objects.filter(date_joined__range=(timezone.now(), timezone.now().date())).count()
			elif sort_by=='2': # this-week
				date = timezone.now() - datetime.timedelta(days=7)
				user_count = User.objects.filter(date_joined__range=(date ,start_date)).count()
			elif sort_by=='3': #this-months
				date = datetime.date.today().replace(day=1)
				user_count = User.objects.filter(date_joined__range=(date ,start_date)).count()
			else:# this-year
				date = timezone.now() - datetime.timedelta(days=365)
				user_count = User.objects.filter(date_joined__range=(date ,start_date)).count()
			startdate =''
			enddate =''

		elif startdate and enddate and not sort_by:
			start_date = datetime.datetime.strptime(startdate, '%m/%d/%Y').strftime('%Y-%m-%d')
			end_date = datetime.datetime.strptime(enddate, '%m/%d/%Y').strftime('%Y-%m-%d')+' 23:59:59'
			user_count = User.objects.filter(date_joined__range=(start_date, end_date)).count()
			sort_by = '0'

		else:
			user_count = User.objects.all().count()
		context ={
			'user_count':user_count,
			'total_download':0,
			'startdate':startdate,
			'enddate':enddate,
			'sort_by':sort_by
		}
		return render(request, 'admin_panel/report_generation/report_generation.html', context)


class DownloadCSVView(View):

	def get(self,request):

		total_download = request.GET.get('total_download')
		user_count = request.GET.get('total_users')

		# month = timezone.now() - datetime.timedelta(days=30)
		# posts_by_months = Post.objects.filter(
		# 			created__range=(month, timezone.now())
		# 		).values('created').order_by('created')
		# grouped = itertools.groupby(posts_by_months, lambda d: d.get('created').strftime('%b %d'))
		# posts = dict([(day, len(list(this_day))) for day, this_day in grouped])

		# User.objects.all().annotate(Year=ExtractYear('created')).values('Year').annotate(
		# 	dcount=Count('Year')).order_by()

		# Create the HttpResponse object with the appropriate CSV header.
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="report.csv"'

		writer = csv.writer(response)
		writer.writerow(['Total_download', 'Registered Users'])
		writer.writerow([total_download, user_count])

		return response