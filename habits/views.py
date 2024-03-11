from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from habits.models import Habit
from habits.pagination import HabitPagination
from habits.serializers import HabitSerializer
from habits.tasks import habit_reminder


class HabitViewSet(viewsets.ModelViewSet):
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

    @action(detail=False, methods=['get'])
    def test(self, request, *args, **kwargs):
        res = habit_reminder()
        return Response({'res': res})
