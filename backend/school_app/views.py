from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Student, SubjectMark
from .serializers import StudentListSerializer, StudentDetailSerializer, CorrectionSerializer
from django.db.models import Avg, Sum

class StudentListView(generics.ListAPIView):
    serializer_class = StudentListSerializer

    def get_queryset(self):
        queryset = Student.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

class StudentDetailView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentDetailSerializer
    lookup_field = 'admission_no'

class SummaryView(APIView):
    def get(self, request):
        # Class average and top 5 per subject
        subject_stats = {}
        subjects_list = SubjectMark.objects.filter(marks_obtained__isnull=False).values_list('subject', flat=True).distinct()
        for subject in subjects_list:
            marks = SubjectMark.objects.filter(subject=subject, marks_obtained__isnull=False).select_related('student').order_by('-marks_obtained')
            if marks.exists():
                avg = marks.aggregate(avg_marks=Avg('marks_obtained'))['avg_marks']
                top_5 = [{'name': m.student.name, 'marks': m.marks_obtained} for m in marks[:5]]
                subject_stats[subject] = {
                    'average': round(avg, 1),
                    'top_students': top_5
                }

        # Top students by total marks
        students = Student.objects.annotate(
            total_marks=Sum('marks__marks_obtained')
        ).exclude(total_marks__isnull=True).order_by('-total_marks')
        
        top_students = []
        for s in students[:5]:
            top_students.append({
                'name': s.name,
                'total_marks': s.total_marks,
                'admission_no': s.admission_no
            })

        top_student = top_students[0] if top_students else None

        return Response({
            'subject_stats': subject_stats,
            'top_student': top_student,
            'top_5_students': top_students
        })

class CorrectionsView(APIView):
    def post(self, request):
        serializer = CorrectionSerializer(data=request.data)
        if serializer.is_valid():
            admission_no = serializer.validated_data['admission_no']
            subject = serializer.validated_data['subject']
            marks = serializer.validated_data['marks']

            student = Student.objects.get(admission_no=admission_no)
            mark_obj, created = SubjectMark.objects.get_or_create(
                student=student, subject=subject,
                defaults={'marks_obtained': marks}
            )
            if not created:
                mark_obj.marks_obtained = marks
                mark_obj.save()

            return Response({"status": "success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
