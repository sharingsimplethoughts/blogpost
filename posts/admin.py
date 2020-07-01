from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register([
    Post,
    PostMediaFiles,
    PostLikes,
    Comments,
    CommentLike,
    Images,
    PollPost,
    PollOptions,
    VoteAPoll,
    CompetitionPost,
    CompetitionPrizeImages,
    CompetitionblogByUsers,
    CompetitionEnteredUsers,
    CompetitionWinners,
    SaveAddressForCompetitionPrize,
    CompetitionWinnersPrizeDeliveryStatus,
    CustomersComplains,
    ReportAPost,
    PostUserViewModel,
])
