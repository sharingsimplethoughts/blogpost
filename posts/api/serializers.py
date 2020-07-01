from rest_framework.serializers import(
     ModelSerializer,
     CharField,
     SerializerMethodField,
     BooleanField,
     NullBooleanField,
     Serializer,
     ChoiceField,
     ImageField,
     FileField,
     ListField,
     DateField,
     TimeField,
     ValidationError
     )

from ..models import *
from common.common import CustomBooleanField
from blog.settings import BASE_URL
from django.db.models import Count, F
from collections import Counter
from datetime import date
from datetime import  timedelta


class CreatePostCommonFields(Serializer):
    """
    this is for common fields used durring create posts
    """
    is_18_plus = BooleanField(required=True, error_messages={'invalid':'is_18_plus Must be a valid boolean', 'required': 'is_18_plus key is required', 'blank': 'is_18_plus is required'})
    about = CharField(error_messages={'required': 'about key is required', 'blank': 'about is required'})
    description = CharField(allow_blank=True, error_messages={'required': 'description key is required'})


class CreateTextPostSerializer(ModelSerializer, CreatePostCommonFields):
    link = CharField(allow_blank=True,error_messages={'required': 'link key is required'})

    class Meta:
        model = Post
        fields = ['about', 'description', 'link', 'is_18_plus']


class CreateVideoAudioPostSerializer(ModelSerializer, CreatePostCommonFields):
    post_type = CharField(allow_blank=True, error_messages={'required': 'post_type key is required','blank': 'post_type  is required'})

    class Meta:
        model = Post
        fields = ['about', 'description', 'is_18_plus', 'post_type']


class CreateImagePostSerializer(ModelSerializer, CreatePostCommonFields):
    class Meta:
        model = Post
        fields = ['about', 'description', 'is_18_plus']


class CreatePollPostSerializer(ModelSerializer, CreatePostCommonFields):

    ques = CharField(allow_blank=True, error_messages={'required': 'ques key is required','blank': 'ques field is required'})
    poll_end_value = CharField(error_messages={'required': 'poll_end_value key is required','blank': 'poll_end_value is required'})
    poll_end_type = ChoiceField(choices=PollPost.POLL_END_TYPE, error_messages={'required': 'poll_end_type key is required','blank': 'poll_end_type is required'})
    text_options = ListField(allow_empty=True, required=False,error_messages={'required': 'text_options key is required'})
    image_options = ImageField(required=False, max_length=None,  allow_empty_file=True, error_messages={'required': 'image_options key is required'})

    class Meta:
        model = PollPost
        fields = ['about', 'description', 'is_18_plus', 'ques', 'poll_end_value', 'poll_end_type', 'text_options', 'image_options']

from accounts.api.task import select_winners
class CreateCompetitionSerializer(ModelSerializer, CreatePostCommonFields):
    entry_requirement = CharField(error_messages={'required': 'entry_requirement key is required','blank': 'entry_requirement is required'})
    no_of_winners = CharField(error_messages={'required': 'no_of_winners key is required','blank': 'no_of_winners is required'})
    countdown_time = TimeField(error_messages={'required': 'countdown_time key is required','blank': 'countdown_time is required'})
    personal_msg = CharField(error_messages={'required': 'personal_msg key is required','blank': 'personal_msg is required'})
    prize_delivery_date = DateField(error_messages={'required': 'prize_delivery_date key is required','blank': 'prize_delivery_date is required'})
    entry_video = FileField(error_messages={'required': 'entry_video is required','blank': 'entry_video_date is required'})
    video_thumbnail = ImageField(error_messages={'required': 'video_thumbnail is required','blank': 'video_thumbnail is required'})


    class Meta:
        model = CompetitionPost
        fields = [
            'about',
            'description',
            'is_18_plus',
            'entry_requirement',
            'no_of_winners',
            'countdown_time',
            'personal_msg',
            'prize_delivery_date',
            'entry_video',
            'video_thumbnail'
        ]

    def create(self, validated_data):

        request = self.context['request']
        prize_image = request.FILES.getlist('prize_image', [])
        entry_video  = validated_data.get('entry_video', None)
        video_thumbnail = validated_data.get('video_thumbnail', None)


        if len(prize_image)==0:
            raise ValidationError({'message':'Please provide prize images'})

        if entry_video == None:
            raise ValidationError({'message':'Please provide entry video'})

        if entry_video and not video_thumbnail:
            raise ValidationError({'message': 'Please provide thumbnail with video'})
        print(validated_data['is_18_plus'])
        post_obj = Post.objects.create(created_by=request.user, post_type='6', about=validated_data['about'],
                                       description=validated_data['description'],
                                       is_18_plus=validated_data['is_18_plus'])

        countdown_time =validated_data['countdown_time']
        end_time = timezone.now() + timedelta(hours=countdown_time.hour,minutes=countdown_time.minute,seconds=countdown_time.second)

        comp_obj = CompetitionPost.objects.create(post=post_obj,competition_end_time=end_time, entry_requirement=validated_data['entry_requirement'],
                                                  no_of_winners=validated_data['no_of_winners'],countdown_time=validated_data['countdown_time'],
                                                  personal_msg=validated_data['personal_msg'],prize_delivery_date=validated_data['prize_delivery_date'],
                                                  entry_video=validated_data['entry_video'], video_thumbnail=validated_data['video_thumbnail'])


        for img in prize_image:
            CompetitionPrizeImages.objects.create(prize_images=img, post=post_obj)

        # select winner celery cron job
        select_winners.s(post_obj.id).apply_async(eta=end_time)
        # select_winners.delay(post_obj.id)
        # select_winners(post_obj.id)
        return comp_obj


class VoteAPollSerializer(Serializer):
    post_id = CharField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    poll_option_id = CharField(error_messages={'required': 'poll_option_id key is required', 'blank': 'poll_option_id is required'})


class PostCreatedUserDetail(ModelSerializer):

    profile_image = SerializerMethodField()

    def get_profile_image(self, instance):
        if instance.profile_image:
            return BASE_URL +instance.profile_image.url
        return None

    class Meta:
        model = User
        fields = ['first_name', 'last_name' , 'profile_image']


class PostMediaFilesSerializer(ModelSerializer):
    class Meta:
        model = PostMediaFiles
        fields = ['id', 'file']


def calculate_age(born):
    today = date.today()
    try:
        birthday = born.replace(year=today.year)
    except:  # raised when birth date is February 29 and the current year is not a leap year
        birthday = born.replace(year=today.year, month=born.month + 1, day=1)
    if birthday > today:
        return today.year - born.year - 1
    else:
        return today.year - born.year


class PollOptionsSerializer(ModelSerializer):
    vote_percentage  = SerializerMethodField()
    is_option_selected = SerializerMethodField()
    image_option = SerializerMethodField()

    def get_image_option(self, instance):
        if instance.image_option:
            return instance.image_option.url

    def get_is_option_selected(self, instance):
        user = self.context.get('request').user
        if user.is_authenticated:
            qs = VoteAPoll.objects.filter(post__id=self.context.get('post_id'), created_by=user)
            if qs.exists():
                if qs.first().poll_option.id ==instance.id:
                    return True
            return False
        return False


    def get_vote_percentage(self, instance):
        post = self.context.get('post_id')
        votes = VoteAPoll.objects.filter(post__id = self.context.get('post_id')).values_list('poll_option', flat=True)
        votes_count = Counter(votes)
        if votes_count.get(instance.id, None):
            return round((votes_count[instance.id]/votes.count())*100)
        return 0

    class Meta:
        model = PollOptions
        fields = ['image_option','text_option','id', 'vote_percentage','is_option_selected']


class PollPostHomePageSerializer(ModelSerializer):
    total_votes = SerializerMethodField()
    user_voted_option_id = SerializerMethodField()
    poll_options = SerializerMethodField()
    is_poll_end = SerializerMethodField()
    poll_time_left =SerializerMethodField()

    def get_is_poll_end(self, instance):
        current_time  = timezone.now()
        if current_time > instance.poll_end_date:
            return True
        return False

    def get_poll_time_left(self, instance):
        return instance.get_poll_time_left()

    def get_user_voted_option_id (self, instance):
        user = self.context.get('request').user
        if user.is_authenticated:
            qs = VoteAPoll.objects.filter(post__id=self.context.get('post_id'),created_by=user)
            if qs.exists():
                return str(qs.first().poll_option.id)
            return ''
        return ''
    def get_total_votes(self, instance):
        return VoteAPoll.objects.filter(post__id = self.context.get('post_id')).count()


    def get_poll_options(self,instance):
        if instance.post.is_shared_post:
            option_qs  = PollOptions.objects.filter(post = instance.post.parent_main_post_id)
            post_id = instance.post.parent_main_post_id.id
        else:
            option_qs  = PollOptions.objects.filter(post = instance.post)
            post_id = instance.post.id

        data = PollOptionsSerializer(option_qs, context={'post_id' :post_id, 'request':self.context.get('request') }, many=True).data
        return data


    class Meta:
        model = PollPost
        fields = [

            'ques',
            'poll_end_value',
            'poll_end_type',
            'option_type',
            'poll_options',
            'total_votes',
            'user_voted_option_id',
            'is_poll_end',
            'poll_time_left'

        ]


class CompetitionPrizeImagesSerializer(ModelSerializer):
    class Meta:
        model = CompetitionPrizeImages
        fields = [
            'prize_images'
        ]


class SaveAddressForCompetitionPrizeSerializer(ModelSerializer):
    class Meta:
        model = SaveAddressForCompetitionPrize
        exclude = ['post', 'user']


class PrizeReceivingStatusSerializer(Serializer):
    post_id = CharField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    is_prize_received = BooleanField(error_messages={'required': 'is_prize_received key is required', 'blank': 'is_prize_received is required'})


class WinnersListSerializer(Serializer):
    name = SerializerMethodField()

    def get_name(self, instance):
        return instance.get_full_name()

    class Meta:
        model = User
        fields = ['name']


class CompetetionHomePageSerializer(ModelSerializer):
    prize_images = SerializerMethodField()

    time_left = SerializerMethodField()
    is_blog = SerializerMethodField()
    is_entered = SerializerMethodField()
    is_competetion_end = SerializerMethodField()
    competition_winners  =SerializerMethodField()
    time_after_comp_end = SerializerMethodField()

    def get_competition_winners(self, instance):
        qs = CompetitionWinners.objects.filter(post=instance.post).prefetch_related('winners')
        if qs.exists():
            return WinnersListSerializer(qs.first().winners.all(), many=True).data
        return []

    def get_time_after_comp_end(self, instance):
        return instance.get_time_after_comp_end()

    def get_is_competetion_end(self, instance):
        if timezone.now() > instance.competition_end_time:
            return True
        return False

    def get_is_blog(self, instance):
        user = self.context.get('request').user
        if user.is_authenticated:
            if instance.post.is_shared_post:
                blog_qs = CompetitionblogByUsers.objects.filter(post=instance.post.parent_main_post_id, blog_by=user)
            else:
                blog_qs = CompetitionblogByUsers.objects.filter(post=instance.post, blog_by=user)
            if blog_qs.exists():
                return True
        return False

    def get_is_entered(self, instance):
        user = self.context.get('request').user
        if user.is_authenticated:
            if instance.post.is_shared_post:
                enter_qs = CompetitionEnteredUsers.objects.filter(post=instance.post.parent_main_post_id, entered_by=user)
            else:
                enter_qs = CompetitionEnteredUsers.objects.filter(post=instance.post, entered_by=user)
            if enter_qs.exists():
                return True
        return False


    def get_time_left(self, instance):
        if  timezone.now() < instance.competition_end_time:
            abc = ((instance.competition_end_time).replace(microsecond=0) -timezone.now().replace(microsecond=0))
            return  round(abc.total_seconds())
        return 0


    def get_prize_images(self, instance):
        qs =  CompetitionPrizeImages.objects.filter(post=self.context.get('post_id'))
        if qs.first():
            return qs.first().prize_images.url


    class Meta:
        model = CompetitionPost
        fields = [

            'no_of_winners',
            'countdown_time',
            'entry_video',
            'video_thumbnail',
            'blog_by',
            'entered_by',
            'prize_images',
            'time_left',
            'prize_delivery_date',
            'entry_requirement',
            'is_blog',
            'is_entered',
            'blog_by',
            'entered_by',
            'is_competetion_end',
            'competition_winners',
            'time_after_comp_end'
        ]



class CommentsListSerializer(ModelSerializer):
    is_liked = SerializerMethodField()
    comment_by = PostCreatedUserDetail()
    created = SerializerMethodField()
    def get_is_liked(self, instance):
        if self.context.get('request'):
            qs = CommentLike.objects.filter(comment_id=instance, liked_by= self.context.get('request').user)
            if qs.exists():
                return True
            return False
        return False

    def get_created(self, instance):
        return instance.get_created_time()


    class Meta:
        model = Comments
        fields = [
            'id',
            'comment_by',
            'content',
            'created',
            'total_like',
            'is_liked'
        ]


class HomePageSerilizer(ModelSerializer):
    created_by = PostCreatedUserDetail()
    created = SerializerMethodField()
    images = SerializerMethodField()
    audio = SerializerMethodField()
    video = SerializerMethodField()
    is_blur = SerializerMethodField()
    poll = SerializerMethodField()
    created_date_time = SerializerMethodField()
    competition =  SerializerMethodField()
    comments = SerializerMethodField()
    is_liked = SerializerMethodField()
    is_reported = SerializerMethodField()
    is_user_shared = SerializerMethodField()
    is_commented = SerializerMethodField()
    share_detail = SerializerMethodField()


    def get_share_detail(self, instance):
        if instance.is_shared_post:
            data = SharePostDetailSerializer(instance.parent_post_id, context=self.context.get('request')).data
            return data
        return {}
    def get_is_commented(self, instance):
        if self.context.get('request').user:
            qs = Comments.objects.filter(post_id=instance,comment_by=self.context.get('request').user )
            if qs.exists():
                return True
            return False
        return False


    def get_is_user_shared(self, instance):
        if self.context.get('request').user:
            qs = Post.objects.filter(is_shared_post=True, parent_post_id=instance)
            if qs.exists():
                return True
            return False
        return False

    def get_is_reported(self, instance):
        if self.context.get('request').user:
            qs = ReportAPost.objects.filter(post=instance, user = self.context.get('request').user)
            if qs.exists():
                return True
            return False
        return False

    def get_comments(self, instance):
        if self.context.get('is_detail_page'):
            comments_qs = Comments.objects.filter(post_id=instance).order_by('-created')
        else:
            comments_qs = Comments.objects.filter(post_id=instance).order_by('-created')[:2]
        return CommentsListSerializer(comments_qs, context={'request':self.context.get('request')}, many=True).data

    def get_is_liked(self, instance):
        if self.context.get('request'):
            qs = PostLikes.objects.filter(post_id=instance, liked_by = self.context.get('request').user)
            if qs.exists():
                return True
            return False
        return False

    def get_competition(self, instance):
        if instance.post_type=='6':
            compt_qs = CompetitionPost.objects.filter(post=instance)
            if compt_qs.exists():
                data =  CompetetionHomePageSerializer(compt_qs.first(), context={'post_id':instance.id, 'request':self.context.get('request')}).data
                return data
            return {}
        return {}


    def get_created_date_time(self,instance):
        return instance.created

    def get_poll(self, instance):
        if instance.post_type=='5':
            pollpost_qs = PollPost.objects.filter(post=instance)
            if pollpost_qs.exists():
                data = PollPostHomePageSerializer(pollpost_qs.first(), context={'post_id':instance.id, 'request':self.context.get('request')}).data
                return data
            return {}
        return {}


    def get_is_blur(self, instance):
        is_18_plus = instance.is_18_plus
        request = self.context.get('request')
        user = request.user
        puvm = PostUserViewModel.objects.filter(post=instance,user=user).first()
        if puvm:
            return puvm.is_blur
        if not is_18_plus:
            return False
        
        if request.user.is_authenticated:
            
            if user.birth_date is None or user.birth_date =='':
                return True
            present_age = calculate_age(user.birth_date)
            if present_age > 18:
                return False
            return True
        return True

    def get_video(self, instance):
        if instance.post_type == '3':
            video = PostMediaFiles.objects.filter(post_id=instance)
            if video.exists():
                video_obj = video.first()
                if video_obj.thumbnail:
                    thumnail_url = video_obj.thumbnail.url
                else:
                    thumnail_url =""
                return {"video_url":video_obj.file.url, "thumbnail_url": thumnail_url}
            return {}
        return {}

    def get_audio(self, instance):
        if instance.post_type == '4':
            audio = PostMediaFiles.objects.filter(post_id=instance)
            if audio.exists():
                return audio.first().file.url
            return ""
        return ""

    def get_images(self, instance):
        if instance.post_type=='2':
            images = PostMediaFiles.objects.filter(post_id=instance)
            images_data = PostMediaFilesSerializer(images ,many=True).data
            return images_data
        return []

    def get_created(self, instance):
        return instance.get_date()

    class Meta:
        model = Post
        fields =[
            'id',
            'is_blur',
            'created',
            'created_by',
            'about',
            'description',
            'is_18_plus',
            'link',
            'total_views',
            'total_likes',
            'total_comments',
            'total_shares',
            'images',
            'post_type',
            'video',
            'audio',
            'poll',
            'created_date_time',
            'competition',
            'is_shared_post',
            'parent_post_id',
            'parent_main_post_id',
            'comments',
            'is_liked',
            'is_reported',
            'shared_text',
            'is_user_shared',
            'is_commented',
            'share_detail'

        ]


class HomePagePostDetailSerilizer(ModelSerializer):
    created_by = PostCreatedUserDetail()
    created = SerializerMethodField()
    images = SerializerMethodField()
    audio = SerializerMethodField()
    video = SerializerMethodField()
    is_blur = SerializerMethodField()
    poll = SerializerMethodField()
    created_date_time = SerializerMethodField()
    competition =  SerializerMethodField()
    comments = SerializerMethodField()
    is_liked = SerializerMethodField()
    is_reported = SerializerMethodField()
    is_user_shared = SerializerMethodField()
    is_commented = SerializerMethodField()
    share_detail = SerializerMethodField()


    def get_share_detail(self, instance):
        if instance.is_shared_post:
            data = SharePostDetailSerializer(instance.parent_post_id, context=self.context.get('request')).data
            return data
        return {}
    def get_is_commented(self, instance):
        if self.context.get('request').user:
            qs = Comments.objects.filter(post_id=instance,comment_by=self.context.get('request').user )
            if qs.exists():
                return True
            return False
        return False


    def get_is_user_shared(self, instance):
        if self.context.get('request').user:
            qs = Post.objects.filter(is_shared_post=True, parent_post_id=instance)
            if qs.exists():
                return True
            return False
        return False

    def get_is_reported(self, instance):
        if self.context.get('request').user:
            qs = ReportAPost.objects.filter(post=instance, user = self.context.get('request').user)
            if qs.exists():
                return True
            return False
        return False

    def get_comments(self, instance):
        if self.context.get('is_detail_page'):
            comments_qs = Comments.objects.filter(post_id=instance).order_by('-created')
        else:
            comments_qs = Comments.objects.filter(post_id=instance).order_by('-created')[:2]
        return CommentsListSerializer(comments_qs, context={'request':self.context.get('request')}, many=True).data

    def get_is_liked(self, instance):
        if self.context.get('request'):
            qs = PostLikes.objects.filter(post_id=instance, liked_by = self.context.get('request').user)
            if qs.exists():
                return True
            return False
        return False

    def get_competition(self, instance):
        if instance.post_type=='6':
            compt_qs = CompetitionPost.objects.filter(post=instance)
            if compt_qs.exists():
                data =  CompetetionHomePageSerializer(compt_qs.first(), context={'post_id':instance.id, 'request':self.context.get('request')}).data
                return data
            return {}
        return {}


    def get_created_date_time(self,instance):
        return instance.created

    def get_poll(self, instance):
        if instance.post_type=='5':
            pollpost_qs = PollPost.objects.filter(post=instance)
            if pollpost_qs.exists():
                data = PollPostHomePageSerializer(pollpost_qs.first(), context={'post_id':instance.id, 'request':self.context.get('request')}).data
                return data
            return {}
        return {}


    def get_is_blur(self, instance):
        is_18_plus = instance.is_18_plus
        request = self.context.get('request')
        user = request.user
        b=''
        if not is_18_plus:
            b = False
        
        # if request.user.is_authenticated:
        if user.birth_date is None or user.birth_date =='':
            b = True
        present_age = calculate_age(user.birth_date)
        if present_age > 18:
            b = False
        else:
            b = True
        # else:
        #     b = True
        puvm = PostUserViewModel.objects.filter(post=instance,user=user).first()
        if puvm:
            puvm.post=instance
            puvm.user=user
            puvm.is_blur=b
        else:
            puvm = PostUserViewModel(
                post=instance,
                user=user,
                is_blur=b,
            )
        puvm.save()
        return b

    def get_video(self, instance):
        if instance.post_type == '3':
            video = PostMediaFiles.objects.filter(post_id=instance)
            if video.exists():
                video_obj = video.first()
                if video_obj.thumbnail:
                    thumnail_url = video_obj.thumbnail.url
                else:
                    thumnail_url =""
                return {"video_url":video_obj.file.url, "thumbnail_url": thumnail_url}
            return {}
        return {}

    def get_audio(self, instance):
        if instance.post_type == '4':
            audio = PostMediaFiles.objects.filter(post_id=instance)
            if audio.exists():
                return audio.first().file.url
            return ""
        return ""

    def get_images(self, instance):
        if instance.post_type=='2':
            images = PostMediaFiles.objects.filter(post_id=instance)
            images_data = PostMediaFilesSerializer(images ,many=True).data
            return images_data
        return []

    def get_created(self, instance):
        return instance.get_date()

    class Meta:
        model = Post
        fields =[
            'id',
            'is_blur',
            'created',
            'created_by',
            'about',
            'description',
            'is_18_plus',
            'link',
            'total_views',
            'total_likes',
            'total_comments',
            'total_shares',
            'images',
            'post_type',
            'video',
            'audio',
            'poll',
            'created_date_time',
            'competition',
            'is_shared_post',
            'parent_post_id',
            'parent_main_post_id',
            'comments',
            'is_liked',
            'is_reported',
            'shared_text',
            'is_user_shared',
            'is_commented',
            'share_detail'

        ]


class SharePostDetailSerializer(HomePageSerilizer,ModelSerializer):
    class Meta:
        model = Comments
        fields = [
            'created',
            'created_by',

        ]


class TextPostDetailSerializer(HomePageSerilizer, ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id',
            'is_blur',
            'created',
            'created_by',
            'about',
            'description',
            'is_18_plus',
            'link',
            'total_views',
            'total_likes',
            'total_comments',
            'total_shares',
            'post_type',
        ]


class CompetitionDetailSerializer(HomePageSerilizer, ModelSerializer):


    class Meta:
        model = Post
        fields = [
            'id',
            'is_blur',
            'created_by',
            'total_views',
            'total_likes',
            'total_comments',
            'total_shares',
            'about',
            'description',
            'is_18_plus',
            'competition',

        ]


class EditPostDetailSerializer(ModelSerializer):
    images = SerializerMethodField()
    audio = SerializerMethodField()
    video = SerializerMethodField()

    def get_video(self, instance):
        if instance.post_type == '3':
            video = PostMediaFiles.objects.filter(post_id=instance)
            return video.first().file.url
        return ""

    def get_audio(self, instance):
        if instance.post_type == '4':
            audio = PostMediaFiles.objects.filter(post_id=instance)
            return audio.first().file.url
        return ""

    def get_images(self, instance):
        if instance.post_type=='2':
            images = PostMediaFiles.objects.filter(post_id=instance)
            images_data = PostMediaFilesSerializer(images ,many=True).data
            return images_data
        return []

    class Meta:
        model = Post
        fields =[
            'about',
            'description',
            'is_18_plus',
            'link',
            'images',
            'post_type',
            'video',
            'audio'

        ]


class ImageListSerializer(ModelSerializer):
    class Meta:
        model = Images
        fields = ['id' ,'image_url']


class SaveAddressForPrizeSerilizer(ModelSerializer):
    post_id = CharField(error_messages={'required': 'post key is required', 'blank': 'post_id is required'})
    country = CharField(max_length=100, error_messages={'required': 'country key is required', 'blank': 'country is required'})
    street = CharField(max_length=200, error_messages={'required': 'street key is required', 'blank': 'street is required'})
    city = CharField(max_length=100, error_messages={'required': 'city key is required', 'blank': 'city is required'})
    zip_code = CharField(max_length=8,error_messages={'required': 'zip_code key is required', 'blank': 'zip_code is required'})
    country_code = CharField(max_length=4, error_messages={'required': 'country_code key is required', 'blank': 'country_code is required'})
    mobile_number = CharField(max_length=12, error_messages={'required': 'mobile_number key is required', 'blank': 'mobile_number is required'})

    class Meta:
        model = SaveAddressForCompetitionPrize
        fields = [
            'post_id',
            'country',
            'street',
            'city',
            'zip_code',
            'country_code',
            'mobile_number'
        ]


class LikePostSerilizer(Serializer):
    post_id = CharField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    is_liked = BooleanField(error_messages={'required': 'is_liked key is required', 'blank': 'is_liked is required'})


class CommentSerializer(ModelSerializer):
    post_id = CharField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    content = CharField(error_messages={'required': 'content key is required', 'blank': 'content is required'})

    class Meta:
        model = Comments
        fields = [
            'post_id',
            'content',
        ]


class LikeCommentSerilizer(Serializer):
    comment_id = CharField(error_messages={'required': 'comment_id key is required', 'blank': 'comment_id is required'})
    is_liked = BooleanField(error_messages={'required': 'is_liked key is required', 'blank': 'is_liked is required'})


class ReportACommentSerilizer(Serializer):
    post_id = CharField(error_messages={'required': 'post_id key is required', 'blank': 'post_id is required'})
    text = CharField(allow_blank=True,error_messages={'required': 'text key is required'})
    option = CharField(allow_blank=True,error_messages={'required': 'option key is required'})


class CompetetionListHomePageSerializer(CompetetionHomePageSerializer, ModelSerializer):
        id = SerializerMethodField()
        created_by = SerializerMethodField()

        def get_created_by(self, instance):
            return PostCreatedUserDetail(instance.post.created_by).data

        def get_id(self, instance):
            return instance.post.id

        class Meta:
            model = CompetitionPost
            fields =[
                'id',
                'created_by',
                'time_left',
                'is_blog',
                'is_entered'

            ]


class PostListByTypeSerializer(ModelSerializer):
    created_by = PostCreatedUserDetail()

    class Meta:
        model = Post
        fields = [
            'id',
            'created_by'
        ]

