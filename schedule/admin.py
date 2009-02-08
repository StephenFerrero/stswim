from django.contrib import admin
from stswim.schedule.models import Household, Parent, Student, Employee, Season, Lesson, LessonSlot

for model in [Household, Parent, Student, Employee, Season, Lesson, LessonSlot,]:
    admin.site.register(model)
