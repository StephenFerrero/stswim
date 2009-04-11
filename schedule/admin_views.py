from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.views.generic.list_detail import object_list
from django.core.urlresolvers import reverse
from datetime import date
from models import *
from forms import *
from views import *
from stswim.accounts.forms import ParentEditForm

@permission_required('schedule.can_viewfullschedule')
def manageschedule(request):
	#TODO: Get today's lessons based on logged in user, or default to all lessons
	todayslessonslots = LessonSlot.objects.filter(start_datetime__exact = date.today(), status__exact = 'Booked')
	
	#Dashboard search form
	form = PersonSearchForm()
	parents = []
	students =[]
	message = ''
	show_results = False
	#If request has a query attached, process query.
	if request.GET.has_key('query'):
		  show_results = True
		  query = request.GET['query'].strip()
		  if query:
		  	   form = PersonSearchForm({'query' : query})
		  	   q1 = Q(first_name__icontains = query)
		  	   q2 = Q(last_name__icontains = query)
		  	   q3 = q1 | q2
		  	   students = Student.objects.filter(q3)
		  	   parents = Parent.objects.filter(q3)
		  	   
		  	   # Check if query returned any results, if not provide error message.
		  	   if not students:
		  	   	   if not parents:
		  	   	   	   message = 'No people were found matching that query'

		  	   
	variables = RequestContext(request, {'form' : form,
										'parents' : parents,
										'students' : students,
										'show_results' : show_results,
										'message' : message,
										'todayslessonslots' : todayslessonslots })
	if request.GET.has_key('ajax'):
		return render_to_response('schedule/people_list.html', variables)
	else:
		return render_to_response("schedule/base_manage.html", variables,
							  context_instance=RequestContext(request))

@permission_required('schedule.can_viewhousehold')
def viewhousehold(request, household_id):
	household = Household.objects.get(id = household_id)
	household_parents = Parent.objects.filter(household__exact = household)
	household_students = Student.objects.filter(household__exact = household)
	household_lessons = Lesson.objects.filter(students__in = household_students).order_by('lessonslot').distinct()

	
	return render_to_response("schedule/household_detail.html",
								{'household' : household, 'parents' : household_parents, 'students' : household_students,
								 'household_lessons' : household_lessons},
								context_instance=RequestContext(request))

@permission_required('schedule.can_viewstudents')
def liststudents(request):
	students = Student.objects.all()
	return object_list(request, students)

@staff_member_required	
def addstudent(request, household_id):
	if request.method == 'POST':
		form = StudentAddForm(household_id, request.POST)
		if form.is_valid():
			household_id = form.save()
			return HttpResponseRedirect(reverse('view_household', args=[household_id]))
	else:
		form = StudentAddForm(household_id)
	return render_to_response("schedule/manageform.html", {'form' : form, 'form_title' : 'Add Student'}, 
				  context_instance=RequestContext(request))
	
@permission_required('schedule.can_viewstudents')
def viewstudent(request, student_id):
	student = Student.objects.get(id = student_id)
	lessons = Lesson.objects.filter(students__exact = student).order_by('lessonslot')
	return render_to_response("schedule/student_detail.html",
								{'student' : student, 'lessons' : lessons},
								context_instance=RequestContext(request))
	
@staff_member_required
def editstudent(request, student_id):
	student = Student.objects.get(id = student_id)
	if request.method == 'POST':
		form = StudentEditForm(request.POST, instance=student)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('view_student', args=[student_id]))
	else:
		form = StudentEditForm(instance=student)
	return render_to_response("schedule/manageform.html", {'form' : form, 'form_title' : 'Edit Student'}, 
				  context_instance=RequestContext(request))

@staff_member_required
def addstudenttolesson(request, lesson_id):
	lesson = Lesson.objects.get(id = lesson_id)
	lessonslot = lesson.lessonslot_set.all()[0]
	
	if request.method == 'POST':
		form = AddStudentToLessonForm(request.POST)
		if form.is_valid():
			students = form.cleaned_data['students']
			for student in students:
					lesson.addstudent(student)
			
			return HttpResponseRedirect(reverse('view_lessonslot', args=[lessonslot.id]))
	else:
		form = AddStudentToLessonForm()
	form_instructions = 'Select student(s) you wish to add to the lesson'
	
	return render_to_response("schedule/manageform.html", {'form' : form, 'form_title' : 'Add Student To Lesson', 'form_instructions' : form_instructions}, 
				  context_instance=RequestContext(request))

@staff_member_required
def removestudentfromlesson(request, student_id, lesson_id):
	student = Student.objects.get(id = student_id)
	lesson = Lesson.objects.get(id = lesson_id)
	lessonslot = lesson.lessonslot_set.all()[0]
	lesson.removestudent(student)
	return HttpResponseRedirect(reverse('view_lessonslot', args=[lessonslot.id]))

@staff_member_required
def deletelesson(request, lesson_id):
	lesson = Lesson.objects.get(id = lesson_id)
	lessonslot = lesson.lessonslot_set.all()[0]
	
	lesson.cancel()

	return HttpResponseRedirect(reverse('view_lessonslot', args=[lessonslot.id]))
	

@staff_member_required
def editlesson(request, lesson_id):
	lesson = Lesson.objects.get(id = lesson_id)
	lessonslot = lesson.lessonslot_set.all()[0]
	if request.method == 'POST':
		form = LessonEditForm(request.POST, instance=lesson)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('view_lessonslot', args=[lessonslot.id]))
	else:
		form = LessonEditForm(instance=lesson)
	return render_to_response("schedule/manageform.html", {'form' : form, 'form_title' : 'Edit Lesson'}, 
				  context_instance=RequestContext(request))

@staff_member_required
def closeday(request, year, month, day):
	year = int(year)
	month = int(month)
	day = int(day)
	
	d = date(year, month, day)
	
	lessonslots = LessonSlot.objects.filter(date__exact=d)
	
	for lessonslot in lessonslots:
	   lessonslot.close()
	 
	
	return HttpResponseRedirect(reverse('view_season_byday', args=[year, month, day]))

@staff_member_required
def openday(request, year, month, day):
	year = int(year)
	month = int(month)
	day = int(day)
	
	d = date(year, month, day)
	
	lessonslots = LessonSlot.objects.filter(date__exact=d)
	
	for lessonslot in lessonslots:
		lessonslot.open()
		
	return HttpResponseRedirect(reverse('view_season_byday', args=[year, month, day]))

@permission_required('schedule.can_viewparents')
def listparents(request):
	parents = Parent.objects.all()
	return object_list(request, parents)
									
@permission_required('schedule.can_viewparents')
def viewparent(request, parent_id):
	parent = Parent.objects.get(id = parent_id)
	return render_to_response("schedule/parent_detail.html",
								{'parent' : parent},
								context_instance=RequestContext(request))

@staff_member_required
def editparent(request, parent_id):
	parent = Parent.objects.get(id = parent_id)
	if request.method == 'POST':
		form = ParentEditForm(request.POST, instance=parent)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('view_parent', args=[parent_id]))
	else:
		form = ParentEditForm(instance=parent)
	return render_to_response("schedule/manageform.html", {'form' : form, 'form_title' : 'Edit Parent'}, 
				  context_instance=RequestContext(request))

@staff_member_required	
def addseason(request):
	if request.method == 'POST':
		form = AddSeasonForm(request.POST)
		if form.is_valid():
			season_id = form.save()
			return HttpResponseRedirect(reverse('view_season', args=[season_id]))
	else:
		form = AddSeasonForm()
	return render_to_response("schedule/manageform.html", {'form' : form, 'form_title' : 'Add Season'}, 
				  context_instance=RequestContext(request))
	
@staff_member_required
def addlessonslot(request):
	if request.method == 'POST':
		form = AddLessonSlotForm(request.POST)
		if form.is_valid():
			season_id = form.save()
			return HttpResponseRedirect(reverse('view_season', args=[season_id]))
	else:
		form = AddLessonSlotForm()
	return render_to_response("schedule/manageform.html", {'form' : form, 'form_title' : 'Add Lesson Slot'}, 
				  context_instance=RequestContext(request))

@permission_required('schedule.can_viewfullschedule')
def viewlessonslotdetail(request, lessonslot_id):
	lessonslot = LessonSlot.objects.get(id = lessonslot_id)
	return render_to_response("schedule/lessonslot_detail.html",
								{'lessonslot' : lessonslot},
								context_instance=RequestContext(request))

@staff_member_required								
def closelessonslot(request, lessonslot_id):
	lessonslot = LessonSlot.objects.get(id = lessonslot_id)
	lessonslot.close()
	return render_to_response("schedule/lessonslot_detail.html",
								{'lessonslot' : lessonslot},
								context_instance=RequestContext(request))

@staff_member_required								
def openlessonslot(request, lessonslot_id):
	lessonslot = LessonSlot.objects.get(id = lessonslot_id)
	lessonslot.open()
	return render_to_response("schedule/lessonslot_detail.html",
								{'lessonslot' : lessonslot},
								context_instance=RequestContext(request))