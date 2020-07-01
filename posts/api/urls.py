from django.urls import path
from .views import *


urlpatterns = [

    path('create_text_post', CreateTextPostAPIView.as_view(), name="create text post"),
    path('edit_text_post', CreateTextPostAPIView.as_view(), name="edit text post"),

    path('create_image_post', CreateImagePostAPIView.as_view(), name="create image post"),
    path('edit_image_post', CreateImagePostAPIView.as_view(), name="edit image post"),
    path('delete_image_from_post/<int:image_id>', DeleteImagesFromImagesPostAPIView.as_view(), name="delete image from post"),

    path('home_page', HomePageAPIView.as_view(), name="home page"),

    path('create_audio_or_video_post', CreateAudioVideoPostAPIView.as_view(), name="create_audio_video_post"),
    path('edit_audio_or_video_post', CreateAudioVideoPostAPIView.as_view(), name="edit_audio_video_post"),

    path('create_poll', CreatePollPostAPIView.as_view(), name="create_poll"),
    path('vote_in_poll', VoteInPollAPIView.as_view(), name="vote_poll"),

    path('create_competition', CreateCompetitionPostAPIView.as_view(), name="create_competition"),
    path('post_detail/<str:post_id>', PostDetailAPIView.as_view(), name="post_detail_api"),
    path('competition_blog_by', CompetitionblogByPostAPIView.as_view(), name="competition_blog_by"),
    path('competition_entered_by', CompetitionEnteredByPostAPIView.as_view(), name="competition_entered_by"),

    path('winner_detail_page/<str:compt_id>', WinnerDetailPageAPIView.as_view(), name="winner address"),
    path('save_address_for_prize', SaveAddressForPrizeAPIView.as_view(), name="save address"),
    path('update_prize_receiving_status', PrizeReceivingStatusAPIView.as_view(), name="prize receiving status"),
    path('raise_complain', RaiseComplainAPIView.as_view(), name="prize receiving status"),

    path('delete_post/<int:post_id>', DeletePostAPIView.as_view(), name="delete post"),
    path('post_detail/<int:post_id>', PostDetailAPIView.as_view(), name="post post"),
    path('image_list', UploadImageAPIView.as_view(), name="images_list"),
    path('delete_image/<int:id>', UploadImageAPIView.as_view(), name="delete_image"),

    path('like_a_post', LikePostAPIView.as_view(), name="like_post"),
    path('comment_post', CommentOnPostAPIView.as_view(), name="comment_post"),
    path('like_a_comment', LikeACommentPostAPIView.as_view(), name="like_comment"),
    path('report_a_post', ReportAPostAPIView.as_view(), name="report post"),
    path('share_a_post', ShareAPostAPIView.as_view(), name="share_post"),

    path('all_post_list_by_type', PostListByTypeAPIView.as_view(), name="post lists"),

]

