from datetime import datetime
from accounts.models import User
from chat.views import createNode


def update_user():
    users = User.objects.all()
    for user in users:
        createNode(user.first_name, user.last_name, user.id, user.profile_image)
        return True


