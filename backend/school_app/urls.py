from django.urls import path
from .views import StudentListView, StudentDetailView, SummaryView, CorrectionsView

urlpatterns = [
    path('api/students/', StudentListView.as_view(), name='student-list'),
    path('api/students/<str:admission_no>/', StudentDetailView.as_view(), name='student-detail'),
    path('api/summary/', SummaryView.as_view(), name='summary'),
    path('api/marks/corrections/', CorrectionsView.as_view(), name='corrections'),
]
