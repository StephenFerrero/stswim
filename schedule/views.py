from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory, BaseFormSet
from django.shortcuts import render_to_response, redirect
from django.views.generic.simple import direct_to_template
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from stswim.schedule.models import Season, Parent, Student, Lesson, LessonSlot
from forms import *
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import date

@login_required
def requestlesson(request):
	# Allow parents to request lessons
	
    # This class is used to make empty formset forms required
    # See http://stackoverflow.com/questions/2406537/django-formsets-make-first-required/4951032#4951032
	class RequiredFormSet(BaseFormSet):
		def __init__(self, *args, **kwargs):
			super(RequiredFormSet, self).__init__(*args, **kwargs)
			for form in self.forms:
				form.empty_permitted = False

	LessonItemFormset = formset_factory(RequestLessonForm, extra=3, max_num=20, formset=RequiredFormSet)
	
 
	if request.method == 'POST': # If the form has been submitted...
		# Create a formset from the submitted data
		request_lesson_formset = LessonItemFormset(request.POST, request.FILES)
		request_lesson_aux_form = RequestLessonAuxForm(request.POST)
 
		if request_lesson_formset.is_valid() and request_lesson_aux_form.is_valid():
			data = request_lesson_formset.cleaned_data
			note = request_lesson_aux_form.cleaned_data['notes']
			
			#Send confirmation to parent	
			subject1 = 'Lesson Request Received'
			message1 = render_to_string('email/lesson_request_email.txt',
										{ 'data': data, 'note': note})
			
			parent_email = [request.user.email]
			send_mail(subject1, message1, settings.DEFAULT_FROM_EMAIL, parent_email)
			
			#Send request to Candace
			user_id = request.user.id
			parent = Parent.objects.get(user = user_id)
			subject2 = 'New Lesson Request'
			message2 = render_to_string('email/lesson_request_email_management.txt',
										{ 'data': data, 'note': note, 'parent': parent})
			management_email = ['stephenferrero@gmail.com']
			
			send_mail(subject2, message2, settings.DEFAULT_FROM_EMAIL, management_email)
 
			return HttpResponseRedirect('/lessons') #TODO Redirect to a 'success' page
		else:
			return HttpResponseRedirect('/fail') #TODO Failure
	else:
		request_lesson_form = RequestLessonForm()
		request_lesson_formset = LessonItemFormset()
		request_lesson_aux_form  = RequestLessonAuxForm()

	c = {'request_lesson_aux_form': request_lesson_aux_form,
	     'request_lesson_formset': request_lesson_formset,
	     }
 
	return render_to_response('schedule/parent_requestlesson.html', c, context_instance=RequestContext(request))

def regorlogin(request):
	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect("parent_dashboard")
			else:
				return direct_to_template(request, 'inactive_account.html')
		else:
			return direct_to_template(request, 'inactive_account.html')
			
	#Check if user is already logged in, if so send to Parent Dashboard. Otherwise send to Login page.	
	if not request.user.is_authenticated():
		return render_to_response('schedule/regorlogin.html', context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/schedule/parentdashboard/')
	
@login_required
def parentdashboard(request, parent_id=None):
#	if not 1 in request.user.groups.all():
#		return HttpResponseRedirect('/accounts/login/?next=/schedule/parentdashboard')
#	else:
		user_id = request.user.id
		parent = Parent.objects.get(user = user_id)
		students = Student.objects.filter(household__exact = parent.household)
		household_lessons = Lesson.objects.filter(students__in = students).order_by('lessonslot').distinct()
		household_id = parent.household
	
		variables = RequestContext(request, {'parent' : parent,
										'students' : students,
										'household_id' : household_id,
										'user_id' : user_id,
										'household_lessons' : household_lessons})
	
		return render_to_response("schedule/parent_dashboard.html", variables,
						  context_instance=RequestContext(request))

@login_required
def parentregisterstudent(request):
# Allows parents to register students
	user_id = request.user.id
	parent = Parent.objects.get(user = user_id)
	
	if request.method == 'POST':
		form = StudentAddForm(parent.household, request.POST)
		if form.is_valid():
			user = form.save()
			email = form.cleaned_data['email']
			message = "Successfully registered student(s)"
			return render_to_response("schedule/parent_dashboard.html", {'message' : message}, context_instance=RequestContext(request))
	else:
		form = StudentAddForm(parent.household.id)	
	return render_to_response("schedule/parent_registration_form.html", {'form' : form})

def viewseason(request, season_id=None, display_month=None):
	if not season_id:
		today = date.today()
		try:
			#TODO This get statement does not work between seasons.
			season = Season.objects.get(end_date__gte = today)
		except:
			#TODO print error here
			error = "No Season Exists!"
			return render_to_response("error.html",
										{'error' : error,})
		
	else:
		season = Season.objects.get(id = season_id)
	
	return render_to_response("schedule/seasonview.html", 
								{'season' : season, 
								'display_month' : display_month},
								context_instance=RequestContext(request))
	
def viewday(request, year, month, day):

	year = int(year)
	month = int(month)
	day = int(day)

	display_date = date(year, month, day)
	
	season = Season.objects.get(start_date__lte = display_date, end_date__gte = display_date)

	todayslessonslots = LessonSlot.objects.filter(start_datetime__year = display_date.year, start_datetime__month = display_date.month,
													start_datetime__day = display_date.day, status__exact = 'Booked')
	
	return render_to_response("schedule/dayview.html", 
								{'display_date' : display_date, 'todayslessonslots' : todayslessonslots, 'season' : season},
								context_instance=RequestContext(request))

#TODO: (permit only members of same household to view student
@login_required								
def viewstudent(request, student_id):
	student = Student.objects.get(id = student_id)
	
	return render_to_response("schedule/student_detail.htm")