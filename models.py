# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountsEthnicity(models.Model):
    country_name = models.CharField(max_length=100)
    flag = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'accounts_ethnicity'


class AccountsLanguages(models.Model):
    lang_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'accounts_languages'


class AccountsProfileviewscountrecord(models.Model):
    created = models.DateTimeField()
    profile_blog_by = models.ForeignKey('AccountsUser', models.DO_NOTHING)
    profile_blog_to = models.ForeignKey('AccountsUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_profileviewscountrecord'


class AccountsProfileviewsrecoard(models.Model):
    created = models.DateTimeField()
    profile_blog_by = models.ForeignKey('AccountsUser', models.DO_NOTHING)
    profile_blog_to = models.ForeignKey('AccountsUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_profileviewsrecoard'


class AccountsRemovefromsuggestionsrecord(models.Model):
    created = models.DateTimeField()
    remove_by = models.ForeignKey('AccountsUser', models.DO_NOTHING)
    remove_to = models.ForeignKey('AccountsUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_removefromsuggestionsrecord'


class AccountsSociallink(models.Model):
    social_link_type = models.CharField(max_length=5)
    link = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'accounts_sociallink'


class AccountsUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    profile_type = models.CharField(max_length=20)
    is_mail_verify = models.IntegerField()
    is_num_verify = models.IntegerField()
    gender = models.CharField(max_length=20)
    birth_date = models.DateField(blank=True, null=True)
    birth_date_privacy = models.CharField(max_length=5)
    nationality = models.CharField(max_length=50)
    bio = models.TextField()
    profile_image = models.CharField(max_length=100)
    device_token = models.CharField(max_length=500)
    device_type = models.CharField(max_length=5)
    account_type = models.CharField(max_length=500)
    social_id = models.CharField(max_length=500, blank=True, null=True)
    cover_image = models.CharField(max_length=100)
    profile_views_count = models.PositiveIntegerField()
    nationality_key = models.CharField(max_length=20)
    is_private_account = models.IntegerField()
    message_privacy = models.CharField(max_length=20)
    post_privacy = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'accounts_user'
        unique_together = (('account_type', 'social_id'),)


class AccountsUserGroups(models.Model):
    user = models.ForeignKey(AccountsUser, models.DO_NOTHING)
    group = models.ForeignKey('AuthGroup', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_user_groups'
        unique_together = (('user', 'group'),)


class AccountsUserLanguage(models.Model):
    user = models.ForeignKey(AccountsUser, models.DO_NOTHING)
    languages = models.ForeignKey(AccountsLanguages, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_user_language'
        unique_together = (('user', 'languages'),)


class AccountsUserUserPermissions(models.Model):
    user = models.ForeignKey(AccountsUser, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_user_user_permissions'
        unique_together = (('user', 'permission'),)


class AccountsUserViewers(models.Model):
    user = models.ForeignKey(AccountsUser, models.DO_NOTHING)
    viewingandviewers = models.ForeignKey('AccountsViewingandviewers', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_user_viewers'
        unique_together = (('user', 'viewingandviewers'),)


class AccountsUserViewing(models.Model):
    user = models.ForeignKey(AccountsUser, models.DO_NOTHING)
    viewingandviewers = models.ForeignKey('AccountsViewingandviewers', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_user_viewing'
        unique_together = (('user', 'viewingandviewers'),)


class AccountsUsercontactinfo(models.Model):
    current_city = models.CharField(max_length=100)
    current_city_privacy = models.CharField(max_length=5)
    hometown = models.CharField(max_length=100)
    hometown_privacy = models.CharField(max_length=5)
    alt_mobile_number = models.CharField(max_length=20)
    country_code = models.CharField(max_length=10)
    website_link = models.CharField(max_length=100)
    user_id = models.ForeignKey(AccountsUser, models.DO_NOTHING, unique=True)
    current_city_lat = models.CharField(max_length=100)
    current_city_long = models.CharField(max_length=100)
    hometown_lat = models.CharField(max_length=100)
    hometown_long = models.CharField(max_length=100)
    skype_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'accounts_usercontactinfo'


class AccountsUsercontactinfoEthnicity(models.Model):
    usercontactinfo = models.ForeignKey(AccountsUsercontactinfo, models.DO_NOTHING)
    ethnicity = models.ForeignKey(AccountsEthnicity, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_usercontactinfo_ethnicity'
        unique_together = (('usercontactinfo', 'ethnicity'),)


class AccountsUsercontactinfoSocialLink(models.Model):
    usercontactinfo = models.ForeignKey(AccountsUsercontactinfo, models.DO_NOTHING)
    sociallink = models.ForeignKey(AccountsSociallink, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'accounts_usercontactinfo_social_link'
        unique_together = (('usercontactinfo', 'sociallink'),)


class AccountsUsereducationaldetails(models.Model):
    college_name = models.CharField(max_length=200)
    college_since = models.DateField(blank=True, null=True)
    secondary_school = models.CharField(max_length=100)
    sec_class_year = models.PositiveSmallIntegerField(blank=True, null=True)
    high_school = models.CharField(max_length=100)
    high_class_year = models.PositiveSmallIntegerField(blank=True, null=True)
    user_id = models.ForeignKey(AccountsUser, models.DO_NOTHING, unique=True)

    class Meta:
        managed = False
        db_table = 'accounts_usereducationaldetails'


class AccountsUserinterest(models.Model):
    activities = models.CharField(max_length=500)
    hobbies = models.CharField(max_length=500)
    music = models.CharField(max_length=500)
    movies = models.CharField(max_length=500)
    tv_shows = models.CharField(max_length=500)
    games = models.CharField(max_length=500)
    user_id = models.ForeignKey(AccountsUser, models.DO_NOTHING)
    interest_text = models.TextField()

    class Meta:
        managed = False
        db_table = 'accounts_userinterest'


class AccountsUserinterests(models.Model):
    user_id = models.ForeignKey(AccountsUser, models.DO_NOTHING)
    interest = models.CharField(max_length=100)
    interest_type = models.CharField(max_length=5)

    class Meta:
        managed = False
        db_table = 'accounts_userinterests'


class AccountsUserpersonalview(models.Model):
    political_view = models.TextField()
    world_view = models.TextField()
    religious_view = models.TextField()
    user_id = models.ForeignKey(AccountsUser, models.DO_NOTHING, unique=True)

    class Meta:
        managed = False
        db_table = 'accounts_userpersonalview'


class AccountsUserworkexperience(models.Model):
    company_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    work_des = models.TextField()
    is_working_here = models.IntegerField()
    working_since = models.DateField(blank=True, null=True)
    user_id = models.ForeignKey(AccountsUser, models.DO_NOTHING, unique=True)
    location_long = models.CharField(max_length=50)
    location_lat = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'accounts_userworkexperience'


class AccountsViewingandviewers(models.Model):
    status = models.CharField(max_length=50)
    action_date = models.DateTimeField(blank=True, null=True)
    blog_by = models.ForeignKey(AccountsUser, models.DO_NOTHING)
    blog_to = models.ForeignKey(AccountsUser, models.DO_NOTHING)
    created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'accounts_viewingandviewers'


class AdminPanelContactaboutterms(models.Model):
    about_us = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True)
    contact_us = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'admin_panel_contactaboutterms'


class AdminPanelFaq(models.Model):
    query = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'admin_panel_faq'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AccountsUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class SilkProfile(models.Model):
    name = models.CharField(max_length=300)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    time_taken = models.FloatField(blank=True, null=True)
    file_path = models.CharField(max_length=300)
    line_num = models.IntegerField(blank=True, null=True)
    end_line_num = models.IntegerField(blank=True, null=True)
    func_name = models.CharField(max_length=300)
    exception_raised = models.IntegerField()
    dynamic = models.IntegerField()
    request = models.ForeignKey('SilkRequest', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'silk_profile'


class SilkProfileQueries(models.Model):
    profile = models.ForeignKey(SilkProfile, models.DO_NOTHING)
    sqlquery = models.ForeignKey('SilkSqlquery', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'silk_profile_queries'
        unique_together = (('profile', 'sqlquery'),)


class SilkRequest(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    path = models.CharField(max_length=190)
    query_params = models.TextField()
    raw_body = models.TextField()
    body = models.TextField()
    method = models.CharField(max_length=10)
    start_time = models.DateTimeField()
    view_name = models.CharField(max_length=190, blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    time_taken = models.FloatField(blank=True, null=True)
    encoded_headers = models.TextField()
    meta_time = models.FloatField(blank=True, null=True)
    meta_num_queries = models.IntegerField(blank=True, null=True)
    meta_time_spent_queries = models.FloatField(blank=True, null=True)
    pyprofile = models.TextField()
    num_sql_queries = models.IntegerField()
    prof_file = models.CharField(max_length=300)

    class Meta:
        managed = False
        db_table = 'silk_request'


class SilkResponse(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    status_code = models.IntegerField()
    raw_body = models.TextField()
    body = models.TextField()
    encoded_headers = models.TextField()
    request = models.ForeignKey(SilkRequest, models.DO_NOTHING, unique=True)

    class Meta:
        managed = False
        db_table = 'silk_response'


class SilkSqlquery(models.Model):
    query = models.TextField()
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    time_taken = models.FloatField(blank=True, null=True)
    traceback = models.TextField()
    request = models.ForeignKey(SilkRequest, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'silk_sqlquery'
