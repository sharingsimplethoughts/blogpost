from django.db import models
from accounts.models import User
# Create your models here.
from posts.models import CompetitionPost,Post
from django.utils import timezone


class Notifications(models.Model):
    type = models.CharField(max_length=10)
    message = models.CharField(max_length=200)
    created =models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    image = models.CharField(max_length=500)
    user = models.ForeignKey(User, blank=True,null=True, on_delete=models.CASCADE)

    ## for competition type
    post_id = models.ForeignKey(CompetitionPost, related_name="prize_winner_post", on_delete=models.CASCADE, blank=True, null=True)  #competetionPost id

    ## for actions like comment
    post_id_actions = models.ForeignKey(Post, related_name="action_post", on_delete=models.CASCADE, blank=True, null=True)  # for actions


    def get_date(self):
        time = timezone.now()

        if self.created.day == time.day:
            if (time.hour - self.created.hour) == 0:
                minute = time.minute - self.created.minute
                if minute < 1:
                    return "Just Now"
                return str(minute) + " min ago"
            return str(time.hour - self.created.hour) + " hours ago"
        else:
            if self.created.month == time.month:
                return str(time.day - self.created.day) + " days ago"
            else:
                if self.created.year == time.year:
                    return str(time.month - self.created.month) + " months ago"
        return self.created