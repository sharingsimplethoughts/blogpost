from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from common.common import get_error, StandardResultsSetPagination
from django.db.models import F,Q
from django.core.paginator import Paginator
import logging
logger = logging.getLogger('post')
from dateutil.relativedelta import relativedelta
from datetime import  timedelta
from accounts.models import ViewingAndViewers, UserContactInfo
import copy
from accounts.api.task import send_action_notification

def update_user_data(user):
    """
    update post count and last post created for user
    """
    user.post_count = F('post_count') + 1
    user.last_post_created = timezone.now()
    user.save()
    return True

def update_user_data_after_delete_post(user):
    user.post_count = F('post_count') - 1
    post = Post.objects.filter(created_by=user).order_by('-created')
    if post.exists():
        user.last_post_created = post.first().created
    else:
        user.last_post_created = None
    user.save()


class CreateTextPostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        data = request.data
        user = request.user
        post_id = data.get('post_id' ,None)
        if post_id:
            try:
                post = Post.active_posts.get(id=post_id)
            except:
                return Response({
                    'message': 'Invalid post id'
                }, 400)
            serializer = CreateTextPostSerializer(data= data, instance=post, context={'request':request})
            if serializer.is_valid():
                serializer.save(created_by=user, post_type="1")
                return Response({
                    'message': 'Post updated successfully'
                }, 200)

            return Response({'message': get_error(serializer)}, 400)
        else:
            serializer = CreateTextPostSerializer(data= data, context={'request':request})
            if serializer.is_valid():
                serializer.save(created_by=user, post_type="1")
                # update post count and last post created for user
                update_user_data(user)
                return Response({
                    'message':'Post created successfully'
                }, 200)

            return Response({'message':get_error(serializer)},400)


class CreateImagePostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        data = request.data
        user = request.user
        post_id = data.get('post_id' ,None)
        images = request.FILES.getlist('images', [])
        if post_id:
            try:
                post = Post.active_posts.get(id=post_id)
            except:
                return Response({
                    'message': 'Invalid post id'
                }, 400)
            serializer = CreateImagePostSerializer(data= data, instance=post, context={'request':request})
            if serializer.is_valid():
                # check image at least one image is associated with this post
                image_qs = PostMediaFiles.objects.filter(post_id=post_id)
                if not image_qs.exists() and images==[]:
                    return Response({
                        'message': 'There are no image in this post please select at least one image'
                    })
                obj = serializer.save()
                for image in images:
                    PostMediaFiles.objects.create(file=image, post_id=obj)
                return Response({
                    'message': 'Post updated successfully'
                }, 200)

                return Response({'message': get_error(serilizer)}, 400)

        else:
            serilizer = CreateImagePostSerializer(data= data, context={'request':request})
            if serilizer.is_valid():
                if len(images)==0:
                    return Response({
                        'message': 'Please provide at least one image'
                    }, 400)
                obj = serilizer.save(created_by=user, post_type="2")
                for image in images:
                    PostMediaFiles.objects.create(file=image, post_id=obj)
                update_user_data(user)
                return Response({
                    'message':'Post created successfully'
                }, 200)

            return Response({'message':get_error(serilizer)}, 400)


class CreateAudioVideoPostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        data = request.data
        user = request.user
        media_file = request.FILES.get('media_files', None)
        video_thumbnail = request.FILES.get('thumbnail', None)
        post_id = data.get('post_id', None)
        if post_id:
            try:
                post = Post.active_posts.get(id=post_id)
            except:
                return Response({
                    'message': 'Invalid post id'
                }, 400)
            serializer = CreateVideoAudioPostSerializer(data=data, instance=post, context={'request': request})
            if serializer.is_valid():
                obj = serializer.save()
                if  media_file:
                    # check for video thumbnail
                    if not video_thumbnail and data.get("post_type")=='3':
                        return Response({
                            'message': 'Please provide thumbnail of media file'
                        }, 400)
                    # delete previous media file
                    PostMediaFiles.objects.get(post_id=post_id).delete()
                     # upload latest media file
                    PostMediaFiles.objects.create(file=media_file, post_id=obj)

                return Response({
                    'message': 'Post updated successfully'
                }, 200)

            return Response({'message': get_error(serializer)}, 400)
        else:

            serializer = CreateVideoAudioPostSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                if not media_file:
                    return Response({
                        'message': 'Please provide  media file'
                    }, 400)
                if not video_thumbnail and data.get("post_type")=='3':
                    return Response({
                        'message': 'Please provide thumbnail of media file'
                    }, 400)
                obj = serializer.save(created_by=user, post_type=data.get("post_type"))
                PostMediaFiles.objects.create(file=media_file, post_id=obj, thumbnail =video_thumbnail)

                update_user_data(user)
                return Response({
                    'message': 'Post created successfully'
                }, 200)

            return Response({'message': get_error(serializer)}, 400)


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



# calculate date time from day, hour, week, month
def calculate_date_time(val,type):
    current_time = timezone.now()

    if type=='second':
        final_time = current_time + timedelta(seconds=val)
        return final_time

    if type=='minute':
        final_time = current_time + timedelta(minutes=val)
        return final_time

    if type=='hour':
        final_time = current_time + timedelta(hours=val)
        return final_time

    if type=='day':
        final_time = current_time + timedelta(days=val)
        return final_time

    if type == 'week':
        final_time = current_time + timedelta(weeks=val)
        return final_time

    if type == 'month':
        final_time = current_time + relativedelta(months=+val)
        return final_time

    if type == 'year':
        final_time = current_time + relativedelta(years=+val)
        return final_time




class CreatePollPostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):

        data = request.data
        logger.debug(data)
        post_id = data.get('post_id', None)
        image_options = request.FILES.getlist('image_options', [])
        text_options = data.getlist('text_options', [])
        if len(image_options) ==0 and len(text_options) <2:
            return Response({
                'message': 'Please provide at least two options'
            },400)
        if int(data['poll_end_value'])<1:
            raise ValidationError({'message': 'Poll end time should be greater than Zero'})
        if post_id: # for update of post
            # try:
            #     post = Post.active_posts.get(id=post_id)
            # except:
            #     return Response({
            #         'message': 'Invalid post id'
            #     }, 400)
            # serializer = CreatePollPostSerializer(data=data, context={'request': request})
            # if serializer.is_valid():
            #
            #     if len(image_options) == 0 and len(text_options)==0:
            #         return Response({
            #             'message': 'Please provide  image option or text option'
            #         }, 400)
            #     post_obj = Post.objects.create(created_by=request.user, post_type='5', about=data['about'],
            #                         description=data['description'], is_18_plus=serilizer.data['is_18_plus'])
            #
            #
            #     poll_obj = PollPost.objects.create(post=post_obj, ques=data['ques'], poll_end_value=data['poll_end_value'],
            #                             poll_end_type=data['poll_end_type'])
            #
            #     ## save options
            #     if len(image_options) >0:
            #         for option in image_options:
            #             PollOptions.objects.create(image_option=option, post=poll_obj)
            #     else:
            #         for option in text_options:
            #             PollOptions.objects.create(text_option=option, post=poll_obj)
            #             poll_obj.option_type = '2'
            #             poll_obj.save()


                return Response({
                    'message': 'Post updated successfully'
                }, 200)

                return Response({'message': get_error(serilizer)}, 400)
        else:
            serilizer = CreatePollPostSerializer(data=data, context={'request': request})
            if serilizer.is_valid():

                if len(image_options) == 0 and len(text_options)==0 and text_options==['']:
                    return Response({
                        'message': 'Please provide  image option or text option',
                        'data': serilizer.data
                    }, 400)
                post_obj = Post.objects.create(created_by=request.user, post_type='5', about=data['about'],
                                    description=data['description'], is_18_plus=serilizer.data['is_18_plus'])

                calculate_date  =calculate_date_time(int(data['poll_end_value']), data['poll_end_type'])
                poll_obj = PollPost.objects.create(post=post_obj, ques=data['ques'], poll_end_value=data['poll_end_value'],
                                        poll_end_type=data['poll_end_type'],poll_end_date=calculate_date)

                ## save options
                if len(image_options) >0:
                    for option in image_options:
                        PollOptions.objects.create(image_option=option, post=post_obj)
                else:
                    for option in text_options:
                        PollOptions.objects.create(text_option=option, post=post_obj)
                        poll_obj.option_type = '2'
                        poll_obj.save()
                # update post count and last post created for user
                update_user_data(request.user)
                return Response({
                    'message': 'Post created successfully'
                }, 200)

            return Response({'message': get_error(serilizer),'data':serilizer.data}, 400)


class CreateCompetitionPostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        data =  request.data
        post_id = request.data.get('post_id')
        if post_id:
            # update post code
            return Response({
                'message': 'Post updated successfully'
            }, 200)
        else:
            # create new post
            serializer = CreateCompetitionSerializer(data=data, context={'request': request})
            if serializer.is_valid():

                serializer.save()


                # update post count and last post created for user
                update_user_data(request.user)
                return Response({
                    'message': 'Post created successfully'
                }, 200)

            # return Response({'message': serializer.errors}, 400)
            return Response({'message': get_error(serializer)}, 400)


class VoteInPollAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = VoteAPollSerializer(data=request.data ,context={'request': request})
        if serializer.is_valid():

            try:
                post_obj = Post.objects.get(id=request.data['post_id'])
                if post_obj.is_shared_post:
                    post_obj = post_obj.parent_main_post_id
            except:
                return Response({
                    'message': 'Invalid post id'
                }, 400)
            try:
                poll_option = PollOptions.objects.get(post = post_obj,id=request.data['poll_option_id'])
            except:
                return Response({
                    'message': 'invalid option id'
                }, 400)
            #  check poll end
            poll_post_obj = PollPost.objects.get(post=post_obj)
            if poll_post_obj.poll_end_date < timezone.now():
                raise ValidationError({'message': 'Sorry Poll has already end'})

            # check voted or not
            try:
                vote_poll_obj =  VoteAPoll.objects.get(created_by=request.user, post=post_obj)

                vote_poll_obj.poll_option=poll_option
                vote_poll_obj.save()
                message='Your vote Changed successfully'
            except:
                VoteAPoll.objects.create(created_by=request.user,post=post_obj,poll_option=poll_option )
                message= 'Your vote submitted successfully'

            # send new data

            poll_option_ids = PollOptions.objects.filter(post=post_obj).values_list('id', flat=True)
            votes = VoteAPoll.objects.filter(post=post_obj).values_list('poll_option', flat=True)
            votes_count = Counter(votes)
            data = []
            for id in poll_option_ids:
                per_data ={}
                if votes_count.get(id, None):
                    per_data['option_id']=id
                    per_data['new_percentage'] = (votes_count[id] / votes.count()) * 100
                    data.append(per_data)
                    continue
                per_data['option_id'] = id
                per_data['new_percentage'] = 0
                data.append(per_data)
            new_data = {'total_votes':votes.count(),'new_poll_data':data}
            return Response({
                'message':message,
                'data':new_data
            },200)
        return Response({'message': get_error(serializer)}, 400)



class UploadImageAPIView(APIView):
    def post(self, resquest):
        data = resquest.FILES.getlist('images', [])
        for image in data:
            Images.objects.create(image_url=image)
        return Response({
            'message': 'uploaded successfully'
        },200)

    def get(self, request, *args, **kwargs):
        page = int(self.request.GET.get('page_number', 1))
        offset = int(self.request.GET.get('offset', 10))
        images_list = Images.objects.all().order_by('-created')
        paginator = Paginator(images_list, offset)
        try:
            qs = paginator.page(page)
        except:
            # If page is out of range (e.g. 9999), deliver last page of results.
            qs = Post.active_posts.none()
        return Response({'data':ImageListSerializer(qs, many=True).data},200)

    def delete(self, request, *args ,**kwargs):
        id = self.kwargs.get('id')
        Images.objects.filter(id=id).delete()
        return Response({
            'message': 'successfully deleted'
        },200)


class HomePageAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]


    serializer_class = HomePageSerilizer

    def get_queryset(self):
        post_type = self.request.GET.get('post_type', 0)
        page = int(self.request.GET.get('page', 1))

        if post_type=='0':
            post_list = Post.active_posts.all().order_by('-created')
            paginator = Paginator(post_list, 10)
            try:
                qs = paginator.page(page)
            except:
                # If page is out of range (e.g. 9999), deliver last page of results.
                qs = Post.active_posts.none()
            return qs

        elif post_type=='2': #image+video
            post_list = Post.active_posts.filter(Q(post_type='2') | Q(post_type='3')).order_by('-created')
            paginator = Paginator(post_list, 10)
            try:
                qs = paginator.page(page)
            except:
                # If page is out of range (e.g. 9999), deliver last page of results.
                qs = Post.active_posts.none()
            return qs

        else:
            post_list =Post.active_posts.filter(post_type=post_type).order_by('-created')
            paginator = Paginator(post_list, 10)
            try:
                qs = paginator.page(page)
            except:
                # If page is out of range (e.g. 9999), deliver last page of results.
                qs = Post.active_posts.none()
            return qs

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        viewing = list(ViewingAndViewers.objects.filter(blog_by = request.user, status='2').values_list('blog_to', flat=True))
        #viewers = list(ViewingAndViewers.objects.filter(blog_to = request.user, status='2').values_list('blog_by', flat=True))

        all_friends = set(viewing)
        # include self
        all_friends.add(request.user.id)
        post = CompetitionPost.objects.filter(post__post_type=6, competition_end_time__gt = timezone.now(), post__is_shared_post=False, post__created_by__in = list(all_friends))[:10]
        comp_data = CompetetionListHomePageSerializer(post, context={'request':request}, many=True).data

        data = {
            'ongoing_compt':comp_data,
            'post_list':response.data
        }
        return Response({
            'data':data
        }, 200)


class DeletePostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        user = request.user
        try:
            Post.active_posts.get(id = post_id, created_by = user).delete()
            # update post data after delete
            update_user_data_after_delete_post(user)
            return Response({
                'message': "successfully deleted"
            }, 200)
        except:
            return Response({
                'message':"invalid post id"
            },400)


class DeleteImagesFromImagesPostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def delete(self, request, *args ,**kwargs):
        data = request.data
        try:
            PostMediaFiles.objects.get(id = self.kwargs.get('image_id')).delete()
            return Response({
                'message': 'deleted successfully'
            }, 200)
        except:
            return Response({
                'message':'Invalid image id'
            }, 400)


class PostDetailAPIView(APIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request, *args, **kwargs):
        try:
            post = Post.active_posts.get(id = self.kwargs.get('post_id'))
        except:
            return Response({
                'message': 'Invalid post id'
            }, 400)

        data = HomePagePostDetailSerilizer(post, context={'request':request,'is_detail_page':True}).data
        return Response({
            'data': data
        }, 200)




class CompetitionblogByPostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self,request):
        post_id = request.data.get('post_id')
        try:
            post = Post.active_posts.get(id=post_id, post_type='6')
            if post.is_shared_post:
                main_post = post.parent_main_post_id
            else:
                main_post = post
            obj,created = CompetitionblogByUsers.objects.get_or_create(post=main_post, blog_by=request.user)
            if created:
                comp_obj = CompetitionPost.objects.get(post=main_post)
                comp_obj.blog_by = F('blog_by')+1
                comp_obj.save()
                CompetitionPost.objects.filter(post__parent_main_post_id=main_post,post__is_shared_post=True).update(blog_by=comp_obj.blog_by)

            return Response({
                'message':'blog successfully'
            }, 200)
        except:
            raise ValidationError({'message':'invalid post id'})


class CompetitionEnteredByPostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self,request):
        post_id = request.data.get('post_id')
        try:
            post = Post.active_posts.get(id=post_id, post_type='6')


            if post.is_shared_post:
                main_post = post.parent_main_post_id
            else:
                main_post = post

            if main_post.created_by.id==request.user.id:
                return Response({'message':'You can not enter in own competition'},400)

            obj, created = CompetitionEnteredUsers.objects.get_or_create(post=main_post, entered_by=request.user)
            if created:

                comp_obj = CompetitionPost.objects.get(post=main_post)
                comp_obj.entered_by = F('entered_by') + 1
                comp_obj.save()
                # update all shared posts
                CompetitionPost.objects.filter(post__parent_main_post_id=main_post).update(entered_by=comp_obj.entered_by)

                ## do something after entering in competition
                # 1. share post on his time line

                comp_obj = CompetitionPost.objects.get(post=main_post)
                comp_imgs = CompetitionPrizeImages.objects.filter(post=main_post)
                if post.is_shared_post:
                    parent_main_post_id = post.parent_main_post_id
                else:
                    parent_main_post_id = post
                share_post = Post.objects.create(created_by=request.user, post_type=post.post_type, about=post.about,description=post.description,
                                    is_18_plus=post.is_18_plus, is_shared_post = True, parent_post_id=post, parent_main_post_id=parent_main_post_id )

                CompetitionPost.objects.create(post=share_post, entry_requirement = comp_obj.entry_requirement,no_of_winners=comp_obj.no_of_winners,
                                               countdown_time=comp_obj.countdown_time,competition_end_time=comp_obj.competition_end_time,
                                               prize_delivery_date=comp_obj.prize_delivery_date,entry_video=comp_obj.entry_video,
                                               video_thumbnail=comp_obj.video_thumbnail, blog_by=comp_obj.blog_by,entered_by=comp_obj.entered_by)

                for comp_img in comp_imgs:
                    CompetitionPrizeImages.objects.create(post=share_post,prize_images=comp_img.prize_images)

            return Response({
                'message': 'updated successfully'
            }, 200)
        except:
            raise ValidationError({'message':'invalid post id'})


class WinnerDetailPageAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request, *args, **kwargs):
        comp_id = self.kwargs.get('compt_id')
        try:
            comp = CompetitionPost.objects.select_related('post').get(id=comp_id)
        except:
             raise ValidationError({'message': 'invalid competition id'})

        comp_winner = CompetitionWinners.objects.filter(post=comp.post, winners =request.user)
        if not comp_winner.exists():
            raise ValidationError({'message':'You are not winner of this competition'})

        address_obj = SaveAddressForCompetitionPrize.objects.filter(user=request.user, post=comp.post)
        addr_data = SaveAddressForCompetitionPrizeSerializer(address_obj.first()).data

        img = CompetitionPrizeImages.objects.filter(post=comp.post)
        comp_enter_obj = CompetitionEnteredUsers.objects.get(entered_by = request.user,post=comp.post)

        delivery_status_obj = CompetitionWinnersPrizeDeliveryStatus.objects.filter(post=comp.post, user = request.user)
        if delivery_status_obj.exists():
            is_prize_delivered = '2' if delivery_status_obj.first().is_price_received else '3'
            complaint_status = False
            if not is_prize_delivered:
                complaint_status_qs = CustomersComplains.objects.filter(post=comp.post, user=request.user)

                if complaint_status_qs.exists():
                    complaint_status = True

        else:
            is_prize_delivered = '1' # False
            complaint_status = False

        print(comp.prize_delivery_date, timezone.now().date()+timedelta(days=1))

        data = {
            'id': comp.post.id,
            'personal_msg': comp.personal_msg,
            'prize_delivery_date': comp.prize_delivery_date,
            'prize_image': img.first().prize_images.url,
            'competition_entered_date':comp_enter_obj.created.date(),
            'saved_addr': addr_data,
            'is_addr_data':True if address_obj.exists() else False,
            'is_prize_delivery_end':True if comp.prize_delivery_date < (timezone.now().date()+timedelta(days=1)) else False,
            'is_complaint_raised': complaint_status,
            'is_prize_received':is_prize_delivered
        }
        return Response({
            'data': data
        }, 200)


class PrizeReceivingStatusAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        data = request.data

        serializer = PrizeReceivingStatusSerializer(data =data)
        if serializer.is_valid():
            try:
                post = Post.objects.get(id=serializer.validated_data['post_id'], post_type='6')
            except:
                raise ValidationError({'message':'Invalid post id'})

            comp_winner = CompetitionWinners.objects.filter(post=post, winners=request.user)
            if not comp_winner.exists():
                raise ValidationError({'message': 'You are not winner of this competition'})

            obj, created = CompetitionWinnersPrizeDeliveryStatus.objects.get_or_create(post=post,user=request.user)

            if created:
                if serializer.validated_data['is_prize_received']:
                    obj.is_price_received = True
                else:
                    obj.is_price_received = False

                obj.save()

                return Response({
                    'message': 'saved successfully'
                }, 200)

            else:
                if not obj.is_price_received:
                    return Response({
                        'message':'We have already received your Complaint'
                    }, 400)
                return Response({
                    'message': 'You have already received your prize'
                }, 400)

        return Response({
            'message':get_error(serializer)
        }, 400)


class RaiseComplainAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        post_id = request.data.get('post_id')
        text = request.data.get('complain_text')
        option_text = request.data.get('option_text')

        if not post_id or not text or not option_text:
            raise ValidationError({'message': 'Please provide post_id and complain text and option_text'})
        try:
            post = Post.active_posts.get(id=request.data.get('post_id'), post_type='6')
        except:
            raise ValidationError({'message': 'invalid post id'})

        obj, created = CompetitionWinnersPrizeDeliveryStatus.objects.get_or_create(post=post, is_price_received=False, user=request.user,)

        CustomersComplains.objects.create(prize_delivery_status=obj, option_text=option_text, complain_text=text)

        return Response({
            'message':'Complaint registered successfully'
        }, 200)


class SaveAddressForPrizeAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):

        serializer = SaveAddressForPrizeSerilizer(data = request.data)
        if serializer.is_valid():
            try:
                post = Post.active_posts.get(id=request.data.get('post_id'), post_type='6')
            except:
                raise ValidationError({'message': 'invalid post id'})

            serializer.save(post=post, user =request.user)
            # send notification to competition creator

            return Response({
                'message': 'saved successfully'
            }, 200)

        return Response({'message': get_error(serializer)}, 400)


class LikePostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        data = request.data
        serilizer = LikePostSerilizer(data=data)

        if serilizer.is_valid():
            try:
                post = Post.objects.get(id=serilizer.validated_data['post_id'])
            except:
                raise ValidationError({'message': 'Invalid post_id'})
            else:
                if not serilizer.validated_data['is_liked']:
                    try:
                        post_likes = PostLikes.objects.get(post_id=post, liked_by=request.user)
                        post_likes.delete()

                        post.total_likes = F('total_likes') - 1
                        post.save()

                        return Response({
                            'message':'Like Removed successfully',
                        }, 200)
                    except:
                        raise ValidationError({'message': 'first like this post'})

                obj, created = PostLikes.objects.get_or_create(post_id = post, liked_by=request.user)

                if created:
                    post.total_likes = F('total_likes')+1
                    post.save()

                    # send like notification
                    if request.user != post.created_by:
                        send_action_notification(2,post.id,request.user.id)

                return Response({
                    'message': 'Liked successfully',
                }, 200)
        return Response({
            'message': get_error(serilizer)
        }, 400)


class CommentOnPostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer =CommentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                post = Post.objects.get(id=request.data['post_id'])
            except:
                raise ValidationError({'message': 'Invalid post id'})

            content = serializer.validated_data['content']
            serializer.save(comment_by=request.user, post_id=post)
            post.total_comments = F('total_comments')+1
            post.save()

            if request.user != post.created_by:
                send_action_notification(4, post.id, request.user.id)

            return Response({
                'message':'Commented successfully'
            }, 200)
        return Response({
            'message':get_error(serializer)
        }, 400)


class LikeACommentPostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = LikeCommentSerilizer(data=request.data)

        if serializer.is_valid():
            try:
                comment = Comments.objects.get(id=serializer.validated_data['comment_id'])
            except:
                raise ValidationError({'message': 'Invalid comment_id'})
            else:
                if not serializer.validated_data['is_liked']:
                    try:
                        comment_likes = CommentLike.objects.get(comment_id=comment, liked_by=request.user)
                        comment_likes.delete()
                        comment.total_like = F('total_like') - 1
                        comment.save()

                        return Response({
                            'message':'Like Removed successfully',
                        }, 200)
                    except:
                        raise ValidationError({'message': 'first like this post'})

                obj, created = CommentLike.objects.get_or_create(comment_id = comment, liked_by=request.user)

                if created:
                    comment.total_like = F('total_like')+1
                    comment.save()

                    if request.user != comment.comment_by:
                        send_action_notification(5,comment.post_id.id,request.user.id)

                return Response({
                    'message': 'Liked successfully',
                }, 200)

        return Response({
            'message': get_error(serializer)
        }, 400)


class ReportAPostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        serializer = ReportACommentSerilizer(data=request.data)
        if serializer.is_valid():
            try:
                post = Post.objects.get(id=serializer.validated_data['post_id'])
            except:
                raise ValidationError({'message': 'Invalid post id'})
            else:
                obj, created = ReportAPost.objects.get_or_create(post=post, user=request.user)

                obj.text=serializer.validated_data['text']
                obj.option = serializer.validated_data['option']
                obj.save()

                return Response({
                    'message': 'Reported successfully'
                }, 200)

        raise ValidationError({'message': get_error(serializer)})


class ShareAPostAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        shared_text = request.data.get('shared_text','')
        post_id = request.data.get('post_id')

        if post_id:
            try:
                post = Post.objects.select_related('parent_main_post_id').get(id=post_id)
            except:
                raise ValidationError({'message':'Invalid post id'})
            else:
                if post.is_shared_post:
                    main_post = copy.deepcopy(post.parent_main_post_id)
                    old_post_main = copy.deepcopy(post.parent_main_post_id)
                else:
                    main_post = copy.deepcopy(post)
                    old_post_main = copy.deepcopy(post)

                #common attributes
                main_post.pk=None
                main_post.is_shared_post=True
                main_post.total_views=0
                main_post.total_likes = 0
                main_post.total_comments=0
                main_post.total_shares=0
                main_post.shared_text = shared_text
                main_post.parent_post_id=post
                if not post.is_shared_post:
                    main_post.parent_main_post_id = post
                else:
                    main_post.parent_main_post_id = post.parent_main_post_id
                main_post.save()

                if main_post.post_type =='1':
                    pass

                # image post
                elif main_post.post_type =='2':
                    images_qs = PostMediaFiles.objects.filter(post_id=old_post_main)
                    for image in images_qs:
                        image.id =None
                        image.post_id = main_post
                        image.save()
                elif main_post.post_type=='3' or main_post.post_type=='4':
                    media_qs = PostMediaFiles.objects.filter(post_id=old_post_main)
                    for media in media_qs:
                        media.id = None
                        media.post_id = main_post
                        media.save()

                elif main_post.post_type == '5':
                    poll_obj = PollPost.objects.get(post=old_post_main)

                    poll_obj.id = None
                    poll_obj.post = main_post
                    poll_obj.save()


                elif main_post.post_type=='6':
                    comp_obj = CompetitionPost.objects.get(post=old_post_main)
                    comp_imgs = CompetitionPrizeImages.objects.filter(post=old_post_main)

                    comp_obj.id =None
                    comp_obj.post =main_post
                    comp_obj.save()

                    for img in comp_imgs:
                        img.id=None
                        img.post = main_post
                        img.save()
                else:
                    return Response({
                        'message': 'Something went wrong'
                    },500)

                # increase post shares
                post.total_shares = F('total_shares')+1
                post.save()

                # send notification
                if request.user != post.created_by:
                    send_action_notification(3, post.id, request.user.id)

                return Response({'message':'Post shared successfully'}, 200)

        raise ValidationError({'message':'post_id is required'})


class PostListByTypeAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request):
        type = request.GET.get('type')
        user = request.user
        data ={
            'text': [],
            'image': [],
            'video': [],
            'audio': [],
            'poll': [],
            'competition': []
        }

        try:
            current_city = UserContactInfo.objects.get(user_id=user).current_city
        except:
            current_city = ''

        user_with_same_local = set(UserContactInfo.objects.filter(current_city__iexact=current_city).values_list('user_id__id', flat=True))
        user_with_same_national = set(User.objects.filter(nationality=request.user.nationality).values_list('id', flat=True))
        national_not_in_location = user_with_same_national-user_with_same_local
        global_not_local_nat = (set(User.objects.filter(is_active=True).values_list('id',flat=True))-user_with_same_local-user_with_same_national)

        # LOCAL
        if type=='1':
            post_qs = Post.active_posts.filter(created_by__id__in = user_with_same_local).select_related('created_by').annotate(first_name=F('created_by__first_name'), last_name=F('created_by__last_name'), profile_profile=F('created_by__profile_image')).values('id', 'post_type','first_name', 'last_name', 'profile_profile').order_by('total_likes', 'total_comments', 'total_shares')

        # NATIONAL
        elif type =='2':
            post_qs= Post.active_posts.filter(created_by__in=national_not_in_location).annotate(first_name=F('created_by__first_name'), last_name=F('created_by__last_name'), profile_profile=F('created_by__profile_image')).values('id', 'post_type','first_name', 'last_name', 'profile_profile').order_by('total_likes', 'total_comments', 'total_shares')

        # GLOBAL
        elif type=='3':
            post_qs= Post.active_posts.filter(created_by__in=global_not_local_nat).annotate(first_name=F('created_by__first_name'), last_name=F('created_by__last_name'), profile_profile=F('created_by__profile_image')).values('id', 'post_type','first_name', 'last_name', 'profile_profile').order_by('total_likes', 'total_comments', 'total_shares')

        else:
            raise ValidationError({'message':'Invalid type'})

        for post in post_qs:
            if post['post_type'] == '1':
                post['profile_profile'] = BASE_URL+'/media/'+post['profile_profile']
                data['text'].append(post)
            elif post['post_type'] == '2':
                post['profile_profile'] = BASE_URL + '/media/' + post['profile_profile']
                data['image'].append(post)
            elif post['post_type'] == '3':
                post['profile_profile'] = BASE_URL + '/media/' + post['profile_profile']
                data['video'].append(post)
            elif post['post_type'] == '4':
                post['profile_profile'] = BASE_URL + '/media/' + post['profile_profile']
                data['audio'].append(post)
            elif post['post_type'] == '5':
                post['profile_profile'] = BASE_URL + '/media/' + post['profile_profile']
                data['poll'].append(post)
            elif post['post_type'] == '6':
                post['profile_profile'] = BASE_URL + '/media/' + post['profile_profile']
                data['competition'].append(post)
        return Response({
            'data': data
        }, 200)

