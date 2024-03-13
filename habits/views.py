from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from habits.models import Habit
from habits.pagination import HabitPagination
from habits.serializers import HabitSerializer
from habits.tasks import habit_reminder
from habits.yasg import habit_docs, habit_docs_test


class HabitViewSet(viewsets.ModelViewSet):
    __doc__ = habit_docs

    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    pagination_class = HabitPagination

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    @action(detail=False, methods=['get'])
    def published(self, request, *args, **kwargs):
        published_habits = self.queryset.filter(is_public=True)
        page = self.paginate_queryset(published_habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(published_habits, many=True)
        return Response(serializer.data)

    @habit_docs_test
    @action(detail=False, methods=['get'])
    def test(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            if settings.TELEGRAM_ENABLE_TEST_ENDPOINT:
                habit_reminder()
                res = 'Endpoint was called'
            else:
                res = 'Endpoint is disabled'
        else:
            res = 'Only for superusers'
        return Response({'res': res})
