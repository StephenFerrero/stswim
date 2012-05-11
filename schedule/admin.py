from django.contrib import admin
from actions import export_as_csv_action
from stswim.schedule.models import Household, Parent, Student, Employee, Season, Lesson, LessonSlot

class ParentAdmin(admin.ModelAdmin)
	list_display = ('first_name', 'last_name','email','phone_number',)
	actions = [export_as_csv_action("CSV Export", fields=['first_name', 'last_name','email','phone_number','address','address2','city','state','zip_code',])]


for model in [Household, Student, Employee, Season, Lesson, LessonSlot,]:
    admin.site.register(model)
