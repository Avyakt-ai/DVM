# add_cdc_script.py
# To run: python add_cdc_script.py

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acads.settings')
django.setup()

from student.models import Dept, CDC, Course


def add_cdc():
    # Get departments starting with 'A'
    departments_a = Dept.objects.filter(dept__startswith='A')
    course = Course.objects.get(uid="EEE F111")
    # Add CDC for each department and semester 1
    for department in departments_a:
        cdc_entry = CDC.objects.create(dept=department, course=course, sem=2)
    print(f"Done for {course} for one group")

if __name__ == "__main__":
    add_cdc()
