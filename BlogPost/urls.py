"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from accounts.views import activate
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/panel/', include(('admin_panel.urls', 'admin_panel'), namespace="admin-panel")),
    path('api/admin/panel/', include(('admin_panel.api.urls', 'api'), namespace="admin-panel-api")),

    path('api/v1/users/', include(('accounts.api.urls', 'accounts'), namespace="users-api")),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activate,
        name='activate'),  # Email Activation
    path('api/v1/chat/', include(('chat.urls', 'chat'), namespace="chat-api")),
    path('api/v1/post/', include(('posts.api.urls', 'posts'), namespace="posts-api")),
    path('api/v1/notification/', include(('notification.api.urls', 'notification'), namespace="notification-api")),
    url('^', include('django.contrib.auth.urls')),  # email varification
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [url(r'^debug/', include('silk.urls', namespace='silk'))]
