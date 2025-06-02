from django.urls import path, include
from .import views
from rest_framework import routers
from rest_framework_nested.routers import NestedDefaultRouter # type: ignore

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)
#router.register(r'conversations', )
#router.register(r'messages', )

urlpatterns = [
    path('', views.index, name='index'),
    path('', include(router.urls)),
]
