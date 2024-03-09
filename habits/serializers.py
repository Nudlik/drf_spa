from rest_framework import serializers

from habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Habit
        fields = '__all__'

    def create(self, validated_data):
        habit = self.Meta.model.objects.create(**validated_data)
        habit.owner = self.context['request'].user
        return habit
