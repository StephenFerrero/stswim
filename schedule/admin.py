from django.contrib import admin
from stswim.schedule.models import Household, Parent, Student, Employee, Season, Lesson, Lessonslot

for model in [Household, Parent, Student, Employee, Season, Lesson, Lessonslot,]:
    admin.site.register(model)
