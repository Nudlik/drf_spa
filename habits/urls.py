from django.urls import path, include
from rest_framework import routers

from habits import apps
from habits.views import HabitViewSet

app_name = apps.HabitsConfig.name

router = routers.DefaultRouter()
router.register(r'', HabitViewSet, basename='habits')

urlpatterns = [
    path('', include(router.urls))
]
