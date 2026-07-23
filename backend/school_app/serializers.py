from rest_framework import serializers
from .models import Student, SubjectMark
from django.db.models import Avg, Sum

class SubjectMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectMark
        fields = ['subject', 'marks_obtained']

class StudentListSerializer(serializers.ModelSerializer):
    average = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ['admission_no', 'name', 'student_class', 'section', 'dob', 'average']

    def get_average(self, obj):
        avg = obj.marks.filter(marks_obtained__isnull=False).aggregate(Avg('marks_obtained'))['marks_obtained__avg']
        if avg is not None:
            return round(avg, 1)
        return None
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['class'] = rep.pop('student_class')
        return rep

class StudentDetailSerializer(serializers.ModelSerializer):
    marks = SubjectMarkSerializer(many=True, read_only=True)
    average = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['admission_no', 'name', 'student_class', 'section', 'dob', 'marks', 'average', 'total']

    def get_average(self, obj):
        avg = obj.marks.filter(marks_obtained__isnull=False).aggregate(Avg('marks_obtained'))['marks_obtained__avg']
        if avg is not None:
            return round(avg, 1)
        return None

    def get_total(self, obj):
        total = obj.marks.filter(marks_obtained__isnull=False).aggregate(Sum('marks_obtained'))['marks_obtained__sum']
        return total if total is not None else 0
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['class'] = rep.pop('student_class')
        return rep

class CorrectionSerializer(serializers.Serializer):
    admission_no = serializers.CharField()
    subject = serializers.CharField()
    marks = serializers.IntegerField(min_value=0, max_value=100)

    def validate_subject(self, value):
        valid_subjects = ['Maths', 'English', 'Science', 'Social Science', 'Hindi']
        # Also, check existing subjects in DB ideally, but prompt says "one of the five in the data"
        if value not in valid_subjects:
            raise serializers.ValidationError("Invalid subject.")
        return value

    def validate_admission_no(self, value):
        if not Student.objects.filter(admission_no=value).exists():
            raise serializers.ValidationError("Student not found.")
        return value
