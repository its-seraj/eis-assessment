import csv
import os
import re
from datetime import datetime
from django.core.management.base import BaseCommand
from school_app.models import Student, SubjectMark

class Command(BaseCommand):
    help = 'Import students and marks from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'File {csv_file} does not exist'))
            return

        self.stdout.write('Clearing existing data for a clean import...')
        Student.objects.all().delete()

        # Dictionary to store the latest marks and details
        # Key: (admission_no, subject)
        # Value: {'student_data': dict, 'marks_obtained': int or None}
        records = {}
        students_data = {}

        def parse_date(date_str):
            # formats: 2014-03-15, 15/03/2014, 15-Mar-2014
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%b-%y', '%d-%b-%Y', '%d-%m-%Y'):
                try:
                    return datetime.strptime(date_str.strip(), fmt).date()
                except ValueError:
                    pass
            raise ValueError(f"Unknown date format: {date_str}")

        def clean_name(name_str):
            # Trim, Title Case, single spaced
            name = name_str.strip().title()
            return re.sub(r'\s+', ' ', name)

        with open(csv_file, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                admission_no = row['admission_no'].strip()
                subject = row['subject'].strip()
                marks_str = row['marks_obtained'].strip() if row.get('marks_obtained') else ''
                marks_obtained = int(marks_str) if marks_str else None

                # Keep higher marks
                key = (admission_no, subject)
                if key in records:
                    existing_marks = records[key]
                    if marks_obtained is not None:
                        if existing_marks is None or marks_obtained > existing_marks:
                            records[key] = marks_obtained
                else:
                    records[key] = marks_obtained

                if admission_no not in students_data:
                    students_data[admission_no] = {
                        'name': clean_name(row['student_name']),
                        'student_class': row['class'].strip(),
                        'section': row['section'].strip(),
                        'dob': parse_date(row['date_of_birth'])
                    }

        # Bulk create students
        student_objs = []
        for admission_no, data in students_data.items():
            student_objs.append(
                Student(
                    admission_no=admission_no,
                    name=data['name'],
                    student_class=data['student_class'],
                    section=data['section'],
                    dob=data['dob']
                )
            )
        Student.objects.bulk_create(student_objs)

        # Bulk create subject marks
        mark_objs = []
        # get all created students in a dict for faster lookup
        student_map = {s.admission_no: s for s in Student.objects.all()}
        
        for (admission_no, subject), marks in records.items():
            mark_objs.append(
                SubjectMark(
                    student=student_map[admission_no],
                    subject=subject,
                    marks_obtained=marks
                )
            )
        SubjectMark.objects.bulk_create(mark_objs)

        self.stdout.write(self.style.SUCCESS('Successfully imported data'))
