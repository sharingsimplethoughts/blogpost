from django.db import models
from accounts.models import User
# Create your models here.
from django.utils import timezone

import datetime

POST_TYPE = (('1', 'Text'), ('2', 'Image'), ('3', 'Video'), ('4', 'Audio'), ('5', 'Poll'), ('6', 'Competition'))


class  Active_Posts_Manager(models.Manager):
    def get_queruset(self):
        return Post.objects.filter(is_active=True)


class Post(models.Model):
    """
    Save all type of posts
    """
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_user')
    created = models.DateTimeField(auto_now_add=True)
    post_type = models.CharField(max_length=20, choices=POST_TYPE)
    is_active = models.BooleanField(default=True)
    total_views = models.IntegerField(default=0)
    total_likes = models.IntegerField(default=0)
    total_comments = models.IntegerField(default=0)
    total_shares = models.IntegerField(default=0)
    # common attributes
    about = models.TextField()
    description = models.TextField(blank=True)
    is_18_plus = models.BooleanField(default=False)

    # text type posts
    link = models.CharField(max_length=1000, blank=True)

    # manager
    objects = models.Manager()  # The default manager.
    active_posts  = Active_Posts_Manager()


    # share post_informations
    is_shared_post = models.BooleanField(default=False)
    parent_post_id = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True,related_name='parent_post')
    parent_main_post_id = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True,related_name='parent_main_post')
    shared_text = models.TextField(blank=True)

    shared_by = models.ManyToManyField(User,blank=True)

    def __int__(self):
        return self.id

    def get_date(self):
        time = timezone.now()

        if self.created.day == time.day and self.created.month == time.month and self.created.year == time.year:
            if (time.hour - self.created.hour) == 0:
                minute = time.minute - self.created.minute
                if minute < 1:
                    return "Just Now"
                return str(minute) + " min ago"
            return str(time.hour - self.created.hour) + " hours ago"
        else:
            if self.created.month == time.month and self.created.year == time.year:
                return str(time.day - self.created.day) + " days ago"
            else:
                if self.created.year == time.year:
                    return str(time.month - self.created.month) + " months ago"
        return self.created


class PostMediaFiles(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_media')
    file = models.FileField()
    thumbnail = models.ImageField(blank=True,null=True,upload_to='video_thumbnail')

    def __str__(self):
        return str(self.id) +'-' + str(self.post_id.id)


class PostLikes(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='liked_post_id')
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_liked_user')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post_id', 'liked_by')


class Comments(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    comment_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_user')
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    total_like = models.PositiveSmallIntegerField(default=0)

    def get_created_time(self):
        time = timezone.now()

        if self.created.day == time.day and self.created.month == time.month and self.created.year == time.year:
            if (time.hour - self.created.hour) == 0:
                minute = time.minute - self.created.minute
                if minute < 1:
                    return "Just Now"
                return str(minute) + " min ago"
            return str(time.hour - self.created.hour) + " hours ago"
        else:
            if self.created.month == time.month and self.created.year == time.year:
                return str(time.day - self.created.day) + " days ago"
            else:
                if self.created.year == time.year:
                    return str(time.month - self.created.month) + " months ago"
        return self.created


class CommentLike(models.Model):
    comment_id = models.ForeignKey(Comments, on_delete=models.CASCADE, related_name='comments_like')
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_liked_user')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) +'-' + str(self.comment_id.id)

    class Meta:
        unique_together = ('comment_id', 'liked_by')



## not required
class Images(models.Model):
    image_url = models.ImageField(upload_to='images/post')
    created = models.DateTimeField(auto_now_add=True)


class PollPost(models.Model):

    OPTION_TYPE = (('1', 'image'), ('2', 'text'))
    POLL_END_TYPE = (('second', 'second'), ('minute', 'minute'), ('hour', 'hour'), ('day', 'day'), ('week', 'week'), ('month', 'month'), ('year', 'year'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='create_post')
    ques = models.TextField(blank=True)
    #1 week, 2 months
    poll_end_value = models.CharField(max_length=5, blank=True)
    poll_end_type = models.CharField(max_length=50, blank=True, choices=POLL_END_TYPE)
    poll_end_date = models.DateTimeField()
    option_type = models.CharField(max_length=3, default="1" , choices=OPTION_TYPE)


    def get_poll_time_left(self):
        time = timezone.now()

        if time > self.poll_end_date:
            return 'Poll end'

        elif self.poll_end_date.day == time.day and self.poll_end_date.month == time.month and self.poll_end_date.year == time.year:
            if (time.hour - self.poll_end_date.hour) == 0:
                minute = self.poll_end_date.minute - time.minute
                if minute < 1:
                    if time > self.poll_end_date:
                        return 'Poll end'
                    second = self.poll_end_date.second - time.second
                    return 'Poll ends in '+ str(second) + " sec"
                return 'Poll ends in '+ str(minute) + " min"
            return 'Poll ends in '+ str(self.poll_end_date.hour - time.hour) + " hours"
        else:
            # if self.poll_end_date.month == time.month:
            #     return 'Poll ends in '+ str(self.poll_end_date.day-time.day) + " days"
            # else:
            #     if self.poll_end_date.year == time.year:
            #         if self.poll_end_date.month - time.month ==1:
            #             return 'Poll ends in ' + str(abs(self.poll_end_date.day - time.day)) + " days"
            #         return 'Poll ends in '+ str(self.poll_end_date.month-time.month ) + " months"
            #
            #     if self.poll_end_date.year > time.year:
            #         return 'Poll ends in '+ str(self.poll_end_date.year - time.year) + " years"

            time_left = (self.poll_end_date - time).days
            if time_left < 1:
                return 'Poll ends in ' + str((self.poll_end_date - time).seconds//3600) + " hours"
            if  1<time_left<30:
                return 'Poll ends in ' + str(time_left) + " days"
            elif 30<=time_left<365:
                return 'Poll ends in ' + str(round(time_left/30)) + " months"
            elif time_left >= 365 :
                return 'Poll ends in ' + str(round(time_left / 365)) + " years"
            else:
                return 'Poll ends in ' + str(time_left) + " days"

        return self.poll_end_date


class PollOptions(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='poll_post_options')
    image_option = models.ImageField(upload_to='images/poll_option',blank=True, null=True)
    text_option = models.CharField(max_length=200,blank=True)


class VoteAPoll(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='poll_post')
    poll_option = models.ForeignKey(PollOptions, on_delete=models.CASCADE, related_name='vote_poll_post_options')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voted_user')
    created = models.DateTimeField(auto_now_add=True)


class CompetitionPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='create_comp_post')
    entry_requirement = models.TextField(blank = True, null=True)
    no_of_winners = models.CharField(max_length=4, blank=True)
    countdown_time = models.TimeField(max_length=30, blank=True)
    competition_end_time = models.DateTimeField()
    personal_msg = models.TextField(blank=True)
    prize_delivery_date = models.DateField(max_length=5, blank=True)
    entry_video = models.FileField(upload_to='competition_video', blank=True, null=True)
    video_thumbnail = models.ImageField(upload_to='competition_thmbnail', blank=True, null=True)
    blog_by = models.PositiveSmallIntegerField(default=0)
    entered_by = models.PositiveSmallIntegerField(default=0)

    def get_time_after_comp_end(self):
        time = timezone.now()
        if self.competition_end_time > time:
            return 'Competition is running'
        if self.competition_end_time.day == time.day and self.competition_end_time.month == time.month and self.competition_end_time.year == time.year:
            if (time.hour - self.competition_end_time.hour) == 0:
                minute = time.minute - self.competition_end_time.minute
                if minute < 1:
                    return "Just Now"
                return str(minute) + " min ago"
            return str(time.hour - self.competition_end_time.hour) + " hours ago"
        else:
            if self.competition_end_time.month == time.month and self.competition_end_time.year == time.year:
                return str(time.day - self.competition_end_time.day) + " days ago"
            else:
                if self.competition_end_time.year == time.year:
                    return str(time.month - self.competition_end_time.month) + " months ago"
        return self.competition_end_time


class CompetitionPrizeImages(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='compt_post_images')
    prize_images = models.ImageField(upload_to='competition_prize', default='2')


class CompetitionblogByUsers(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='blog_comp_post')
    blog_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_user')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'blog_by')


class CompetitionEnteredUsers(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='entry_comp_post')
    entered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entered_user')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'entered_by')


class CompetitionWinners(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    winners = models.ManyToManyField(User ,blank=True)
    created = models.DateTimeField(auto_now_add=True)


class SaveAddressForCompetitionPrize(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    country = models.CharField(max_length=100)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=30)
    country_code = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=15)


class CompetitionWinnersPrizeDeliveryStatus(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    is_price_received = models.BooleanField(default=False)


class CustomersComplains(models.Model):
    prize_delivery_status  = models.ForeignKey(CompetitionWinnersPrizeDeliveryStatus, on_delete=models.CASCADE)
    complain_text = models.TextField()
    option_text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class ReportAPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    option = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


class PostUserViewModel(models.Model):
    is_blur=models.BooleanField(default=True)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id)