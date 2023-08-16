from rest_framework import serializers
from django_testing.settings import MAX_STUDENTS_PER_COURSE
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "name", "students")

    def validate_students(self, students):
        if len(students) > MAX_STUDENTS_PER_COURSE:
            raise serializers.ValidationError(
                "На курсе не может быть больше 20 студентов"
            )
        return students
