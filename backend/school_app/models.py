from django.db import models

class Student(models.Model):
    admission_no = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    student_class = models.CharField(max_length=50)
    section = models.CharField(max_length=50)
    dob = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.admission_no})"

class SubjectMark(models.Model):
    student = models.ForeignKey(Student, related_name='marks', on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    marks_obtained = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student.admission_no} - {self.subject}"
