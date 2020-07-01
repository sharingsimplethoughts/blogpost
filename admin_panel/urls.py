from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.conf.urls import url,include

urlpatterns = [

    # api for admin panel
    path('api/', include(('admin_panel.api.urls', 'api'), namespace="admin-panel-api")),

    path('login/', AdminLoginView.as_view(),name='admin-login'),
    path('home/', login_required(AdminHomeView.as_view()),name='admin-home'),
    path('logout/',LogoutView.as_view(),name='admin-logout'),

    # password reset by mail

    url(r'^password_reset/$', ResetPasswordView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView, name='password_reset_complete'),

    # change password
    path('change_password/', login_required(ChangePasswordView.as_view()), name='admin-change-password'),

    # admin profile
    path('admin_profile/', login_required(AdminProfileView.as_view()), name='admin-profile'),
    path('admin_profile/edit', login_required(AdminProfileEditView.as_view()), name='admin-profile-edit'),

    # account management

    path('account_management/', login_required(UserListView.as_view()), name='user-list'),
    path('user_detail/<int:profile_id>', login_required(UserdetailView.as_view()), name='admin-user-detail'),

    path('date_filter/', login_required(UserDateFilterView.as_view()),
         name='user-date-filter-list'),
    path('date_filter_notif/', login_required(NotificationDateFilterView.as_view()),
         name='notification-date-filter-list'),
    path('date_filter_report/', login_required(ReportsDateFilterView.as_view()),
         name='notification-date-filter-list'),
    path('sort_users/', login_required(UserSortView.as_view()),
         name='user-sort'),


    # settings management

    path('terms_and_condition/', login_required(TermsAboutContactView.as_view()), name='terms_about_contact'),
    path('about_us/', login_required(CreateAboutUsView.as_view()), name='about_us'),
    # path('contact_us/', login_required(CreateContactUsView.as_view()), name='contact_us'),

    path('faq/', login_required(FAQView.as_view()), name='faq'),
    path('tmc_page', TMCView.as_view(), name='tmc_page'),
    path('about_us_page', AboutUsView.as_view(), name='about_us_page'),

    # post management
    path('post_management', UsersPostListView.as_view(), name='user_list_with_post'),
    # path('post_management/date_filter', UserPostDateFilterView.as_view(), name='user_list_with_post_date_filter'),
    # path('post_management/sort', UserPostSortView.as_view(), name='sort'),

    path('user_posts/<int:user_id>', UsersAllPostListView.as_view(), name='user_post'),
    path('user_posts/sort/<int:user_id>', UserAllPostSortView.as_view(), name='sort_posts'),
    path('user_posts/sort_by_type/<int:user_id>', UserAllPostSortView.as_view(), name='sort_posts'),
    path('post_detail/<int:post_id>', ViewPostDetailView.as_view(), name='post_detail'),
    path('notification/', NotificationView.as_view(), name='send notification'),
    path('notification_list/', NotificationListView.as_view(), name=" notification list"),
    path('reports_list/', ReportsListView.as_view(), name=" reports list"),
    path('report_generation/', ReportsGenerationView.as_view(), name=" reports list"),
    path('download_csv/', DownloadCSVView.as_view(), name='download'),

]