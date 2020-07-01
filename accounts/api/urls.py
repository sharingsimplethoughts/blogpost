from django.urls import path
from .views import *


urlpatterns = [

    path('login', UserLoginAPIView.as_view(), name="login"),
    path('registration', UserCreateAPIView.as_view(), name='registration'),
    path('password_reset', PasswordResetView.as_view(), name='rest_password_reset'),
    path('change_password', ChangePasswordAPIView.as_view(), name='change_password'),
    path('remove_account', RemoveAccountAPIView.as_view(), name='remove_account'),
    path('user_basic_info', UserBasicInfoAPIView.as_view(), name='user_basic_info'),
    path('user_contact_info', UserContactInfoAPIView.as_view(), name='user_contact_info'),
    path('user_educational_detail', UserEducationalDetailsAPIView.as_view(), name='user_educational_detail'),
    path('user_work_experience', UserWorkExperienceAPIView.as_view(), name='user_work_experience'),
    path('user_interest', UserInterestsAPIView.as_view(), name='user_interest'),

    path('user_personal_view', UserPersonalViewAPIView.as_view(), name='user_personal_view'),
    path('otp_varify', UserPhoneVerifyAfterRegisterAPIView.as_view(), name="otp_varify"),
    path('otp_re_generate', OTPReSendForPhoneVerify.as_view(), name="otp_re_generate"),

    path('view_profile', ViewUserProile.as_view(), name="view_profile"),

    path('get_all_user_data', GetAllUserData.as_view(), name="view_profile"),

    path('viewing_viewers_list/<str:frnd_type>', GetViewingListApiView.as_view(), name="viewing_viewers_list"),
    # path('viewers_list', GetAllVewersListApiView.as_view(), name="viewers_list"),
    path('send_view_request_to_own_viewers/<str:user_id>', SendFollowRequestToWiewersAPIView.as_view(), name="send_view_request"),

    path('get_personal_info', SettingsUserPersonalInfo.as_view(), name="personal_info"),
    path('save_personal_info', SettingsUserPersonalInfo.as_view(), name="save_personal_info"),
    path('change_private_account_status', ChangePrivateAccountStatusAPIView.as_view(), name="private_account_status"),
    path('privacy_setting_change', PrivacySettingAPIView.as_view(), name="privacy_setting"),
    path('get_user_all_settings', GetUserSettingsAPIView.as_view(), name="get_setting"),
    path('faq_list', FAQListAPIView.as_view(), name="faq_list"),

    ## follow and unfollow request

    path('send_view_request', SendFollowRequestAPIView.as_view(), name="send_view_request"),
    path('accept_or_reject_request', AcceptOrCancelFollowRequestAPIView.as_view(), name="accept_or_reject_request"),
    path('unview_a_friend', StopViewingAFriend.as_view(), name="Unview_a_friend"),

    path('view_other_user_profile/<int:user_id>', ViewUserProfileAPIView.as_view(), name="view_user_profile"),
    path('view_other_user_friends/<int:user_id>', ViewOtherUserFriendsAPIView.as_view(), name="view_user_profile"),

    path('search_user', HomePageSearchUser.as_view(), name="search_user"),
    path('viewing_requests_and_suggestions', ShowFriendsRequestAndSuggestions.as_view(), name="viewing_requests_and_suggestions"),

    path('send_simple_notification',SendSimpleNotification.as_view(), name="send_simple_notification")
]