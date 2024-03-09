from rest_framework import serializers

from habits.models import Habit
from habits.validators import CheckLinkAndReward


class HabitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Habit
        fields = '__all__'
        validators = [
            CheckLinkAndReward('link_habit', 'reward')
        ]

    def create(self, validated_data):
        habit = self.Meta.model.objects.create(**validated_data)
        habit.owner = self.context['request'].user
        habit.save()
        return habit
