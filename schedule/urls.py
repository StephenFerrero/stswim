from django.conf.urls.defaults import *
from stswim.schedule.forms import AddLessonForm1, AddLessonForm2, AddLessonForm3, AddLessonWizard
from stswim.schedule.models import Household, Parent, Student, Season

seasons = {
	'queryset': Season.objects.all(),
}

urlpatterns = patterns('',
	
	url(r'^season/$', 'stswim.schedule.views.viewseason', name='view_currentseason'),
	url(r'^season/add/$', 'stswim.schedule.admin_views.addseason', name='add_season'),
	url(r'^season/(?P<season_id>\d+)/view/month/(?P<display_month>\d+)/$', 'stswim.schedule.views.viewseason', name='view_season_bymonth'),
	url(r'^season/(?P<season_id>\d+)/view/$', 'stswim.schedule.views.viewseason', name='view_season'),
	url(r'^season/date/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/view/$', 'stswim.schedule.views.viewday', name='view_season_byday'),
	url(r'^season/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/close/$', 'stswim.schedule.admin_views.closeday', name='close_day'),
	url(r'^season/date/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/open/$', 'stswim.schedule.admin_views.openday', name='open_day'),
	
	(r'^lessonslot/add/$', 'stswim.schedule.admin_views.addlessonslot'),
	url(r'^lessonslot/(?P<lessonslot_id>\d+)/view/$', 'stswim.schedule.admin_views.viewlessonslotdetail', name='view_lessonslot'),
	(r'^lessonslot/(?P<lessonslot_id>\d+)/close/$', 'stswim.schedule.admin_views.closelessonslot'),
	(r'^lessonslot/(?P<lessonslot_id>\d+)/open/$', 'stswim.schedule.admin_views.openlessonslot'),
	#(r'^lessonslot/(?P<lessonslot_id>\d+)/addlesson/$', 'stswim.schedule.admin_views.addlesson'),
	
	url(r'^lesson/add/$', AddLessonWizard([AddLessonForm1, AddLessonForm2, AddLessonForm3]), name="add_lesson"),
	url(r'^lesson/(?P<lesson_id>\d+)/addstudent/$', 'stswim.schedule.admin_views.addstudenttolesson', name="add_studenttolesson"),
	url(r'^lesson/(?P<lesson_id>\d+)/removestudent/(?P<student_id>\d+)$', 'stswim.schedule.admin_views.removestudentfromlesson', name="remove_studentfromlesson"),
	url(r'^lesson/(?P<lesson_id>\d+)/delete/$', 'stswim.schedule.admin_views.deletelesson', name="delete_lesson"),
	url(r'^lesson/(?P<lesson_id>\d+)/edit/$', 'stswim.schedule.admin_views.editlesson', name="edit_lesson"),
	
	
	url(r'^household/(?P<household_id>\d+)/view/$', 'stswim.schedule.admin_views.viewhousehold', name='view_household'),
	url(r'^household/(?P<household_id>\d+)/addparent/$', 'stswim.accounts.admin_views.addparent', name='add_parenttohousehold'),
	url(r'^household/(?P<household_id>\d+)/addstudent/$', 'stswim.schedule.admin_views.addstudent', name='add_studenttohousehold'),

	url(r'^parents/$', 'stswim.schedule.admin_views.listparents', name='list_parents'),
	url(r'^parent/add/$', 'stswim.accounts.admin_views.addparent', name='add_parent'),
	url(r'^parent/(?P<parent_id>\d+)/view/$', 'stswim.schedule.admin_views.viewparent', name='view_parent'),
	url(r'^parent/(?P<parent_id>\d+)/edit/$', 'stswim.schedule.admin_views.editparent', name='edit_parent'),
	
	url(r'^students/$', 'stswim.schedule.admin_views.liststudents', name='list_students'),
	url(r'^student/(?P<student_id>\d+)/view/$', 'stswim.schedule.admin_views.viewstudent', name='view_student'),
	url(r'^student/(?P<student_id>\d+)/edit/$', 'stswim.schedule.admin_views.editstudent', name='edit_student'),
	
	url(r'^manage/$', 'stswim.schedule.admin_views.manageschedule', name='manage_schedule'),
)

urlpatterns += patterns('django.views.generic.list_detail',
	url(r'^seasons/$', 'object_list', seasons, name='list_seasons'),
)