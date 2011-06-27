from django.conf import settings
from django import forms
from django.contrib.formtools.wizard import FormWizard
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from stswim.schedule.models import SEX_CHOICES, LESSON_TYPES, LESSON_STATUS, Student, Season, LessonSlot, Lesson, Employee
from dateutil.rrule import *
from datetime import timedelta, datetime

class PersonSearchForm(forms.Form):
	query = forms.CharField(
		label='Enter a name to search for',
		widget = forms.TextInput(attrs={'size': 20})
	)
	
class RequestLessonForm(forms.Form):
	#Allows parents to request lessons
	date = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'datepicker','size':'10'}))
	time = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':'10'}))
	students = forms.CharField(required=False, widget=forms.TextInput(attrs={'size':'30'}))
	lesson_type = forms.ChoiceField(required=False, choices=LESSON_TYPES)

class RequestLessonAuxForm(forms.Form):
	notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'size':'180'}))

class StudentAddForm(forms.Form):
	#Forms takes Household ID to properly assign to new student
	def __init__(self, household_id, *args, **kwargs):
		super(StudentAddForm, self).__init__(*args, **kwargs)

		self.household_id = household_id

	first_name = forms.CharField(max_length=40)
	last_name = forms.CharField(max_length=40)
	birth_date = forms.DateField(help_text='MM/DD/YYYY')
	sex = forms.ChoiceField(choices=SEX_CHOICES, label="Gender")
	#TODO: Only request liabilty form if Admin
	has_liabilityform = forms.BooleanField(label="Has Liability Form", required=False, widget=forms.Select(attrs={'disabled':'disabled'}))

	def save(self):
		new_student = Student()
		new_student.household_id = self.household_id
		new_student.first_name = self.cleaned_data['first_name']
		new_student.last_name = self.cleaned_data['last_name']
		new_student.sex = self.cleaned_data['sex']
		new_student.birth_date = self.cleaned_data['birth_date']
		#TODO: Only request liabilty form if Admin
		new_student.has_liabilityform = self.cleaned_data['has_liabilityform']
		new_student.save()
		
		return new_student.household_id

class StudentEditForm(ModelForm):
	class Meta:
		model = Student

#TODO Need better selection here, maybe autocomplete instead of lisitng all students
class AddStudentToLessonForm(forms.Form):
	students = forms.ModelMultipleChoiceField(Student.objects.all())
	

class AddSeasonForm(forms.Form):
	name = forms.CharField(max_length=30)
	start_date = forms.DateField()
	end_date = forms.DateField()

	def save(self):
		new_season = Season()
		new_season.name = self.cleaned_data['name']
		new_season.start_date = self.cleaned_data['start_date']
		new_season.end_date = self.cleaned_data['end_date']
		new_season.save()
		return new_season.id

#Need to validate against existing lessonslots		
class AddLessonSlotForm(forms.Form):
	"Adds a new lesson slot"
	season = forms.ModelChoiceField(Season.objects.all())
	sun = forms.BooleanField(required=False)
	mon = forms.BooleanField(required=False)
	tue = forms.BooleanField(required=False)
	wed = forms.BooleanField(required=False)
	thu = forms.BooleanField(required=False)
	fri = forms.BooleanField(required=False)
	sat = forms.BooleanField(required=False)
	start_date = forms.DateField()
	end_date = forms.DateField()
	start_time = forms.TimeField(input_formats = settings.TIME_INPUT_FORMATS, help_text='All lessonslots are 30 min.')
	instructor = forms.ModelChoiceField(Employee.objects.filter(status__exact = 'Active'))

	def save(self):
		start_date = self.cleaned_data['start_date']
		end_date = self.cleaned_data['end_date']
		
		selected_weekdays = []
		if self.cleaned_data['sun'] == True:
			selected_weekdays.append(6)
		if self.cleaned_data['mon'] == True:
			selected_weekdays.append(0)
		if self.cleaned_data['tue'] == True:
			selected_weekdays.append(1)
		if self.cleaned_data['wed'] == True:
			selected_weekdays.append(2)
		if self.cleaned_data['thu'] == True:
			selected_weekdays.append(3)
		if self.cleaned_data['fri'] == True:
			selected_weekdays.append(4)
		if self.cleaned_data['sat'] == True:
			selected_weekdays.append(5)
			
		#get a list of days based on form input that should have lesson slots created using dateutil
		days = rrule(WEEKLY, wkst=SU, byweekday=selected_weekdays, dtstart=start_date, until=end_date)

		for d in days:
			#Need to convert start_date to start_datetime so that we can sucessfully compare against existing objects
			start_datetime = datetime(d.year, d.month, d.day, self.cleaned_data['start_time'].hour, self.cleaned_data['start_time'].minute)
			
			#Check for existing LessonSlots, if they exist do nothing.
			if not LessonSlot.objects.filter(season__exact = self.cleaned_data['season'].id, 
										 start_datetime__exact = start_datetime):
				
				new_lessonSlot = LessonSlot()
				new_lessonSlot.season_id = self.cleaned_data['season'].id
				new_lessonSlot.start_datetime = start_datetime
				new_lessonSlot.start_time = start_datetime.time()
				new_lessonSlot.end_datetime = start_datetime + timedelta(minutes=30)
				new_lessonSlot.end_time = new_lessonSlot.end_datetime.time()
				new_lessonSlot.weekday = d.weekday()
				new_lessonSlot.status = 'Open'
				new_lessonSlot.instructor = self.cleaned_data['instructor']
				new_lessonSlot.save()

		return self.cleaned_data['season'].id

#AddLessonWizard Step 0
class AddLessonForm1(forms.Form):
	season = forms.ModelChoiceField(Season.objects.all())
	start_date = forms.DateField(help_text = 'Start date will determine day of week for lessons.')
	end_date = forms.DateField()
	start_time = forms.TimeField(input_formats = settings.TIME_INPUT_FORMATS)
	
	#Override form clean method to check if there are any available lessons before continuing.
	def clean(self):
		start_date = self.cleaned_data['start_date']
		end_date = self.cleaned_data['end_date']
		start_time = self.cleaned_data['start_time']
		
		#Need to convert start_date to start_datetime so that we can sucessfully compare against existing objects
		start_datetime = datetime(start_date.year, start_date.month, start_date.day, start_time.hour, start_time.minute)
		end_datetime = datetime(end_date.year, end_date.month, end_date.day, start_time.hour, start_time.minute)
		
		#Check for available lessonslots				
		available_slots = LessonSlot.objects.filter(season__exact = self.cleaned_data['season'], status__exact = 'Open',
							    start_datetime__gte = start_datetime,
							 	start_datetime__lte = end_datetime,
								start_time__exact = start_time)
								
		if available_slots:
			return self.cleaned_data
		else: 
			raise forms.ValidationError('There are no available lessons within the requested criteria.')

#AddLessonWizard Step 1
class AddLessonForm2(forms.Form):
	#Dynamically create a boolean field for each Lesson Slot matching the criteria from Step 0
	def __init__(self, *args, **kwargs):
		season = kwargs['season']
		start_date = kwargs['start_date']
		end_date = kwargs['end_date']
		start_time = kwargs['start_time']
		weekday = kwargs['start_date'].weekday()
		del kwargs['season']
		del kwargs['start_date']
		del kwargs['end_date']
		del kwargs['start_time']
		
		#Need to convert start_date to start_datetime so that we can sucessfully compare against existing objects
		start_datetime = datetime(start_date.year, start_date.month, start_date.day, start_time.hour, start_time.minute)
		end_datetime = datetime(end_date.year, end_date.month, end_date.day, start_time.hour, start_time.minute)

		super(AddLessonForm2, self).__init__(*args, **kwargs)
		available_slots = LessonSlot.objects.filter(season__exact = season, status__exact = 'Open',
							    start_datetime__gte = start_datetime,
							 	start_datetime__lte = end_datetime,
								start_time__exact = start_time)
		print available_slots
		self.fields['lessonslots'] = forms.ModelMultipleChoiceField(available_slots, widget = forms.CheckboxSelectMultiple, label="Available Lessonslots:")

#AddLessonWizard Step 2
class AddLessonForm3(forms.Form):
	lesson_type = forms.ChoiceField(choices=LESSON_TYPES)
	students = forms.ModelMultipleChoiceField(Student.objects.all())
	status = forms.ChoiceField(choices=LESSON_STATUS)

class AddLessonWizard(FormWizard):

	def get_form(self, step, data=None):

		if step == 1:
			return self.form_list[step](data, prefix=self.prefix_for_step(step), initial=self.initial.get(step, None), 
						    start_date=self.start_date,
						    end_date=self.end_date,
						    start_time=self.start_time,
							season=self.season)

		return self.form_list[step](data, prefix=self.prefix_for_step(step), initial=self.initial.get(step, None))

	def process_step(self, request, form, step):
		#Save data from Step 0 to be used in processing Step 1
		if step == 0:
			form.is_valid()
			self.start_date = form.cleaned_data['start_date']
			self.end_date = form.cleaned_data['end_date']
			self.start_time = form.cleaned_data['start_time']
			self.season = form.cleaned_data['season']

			#Need to convert start_date to start_datetime so that we can sucessfully compare against existing objects
			self.start_datetime = datetime(self.start_date.year, self.start_date.month, self.start_date.day, self.start_time.hour, self.start_time.minute)
			self.end_datetime = datetime(self.end_date.year, self.end_date.month, self.end_date.day, self.start_time.hour, self.start_time.minute)
			
			unavailable_slots = LessonSlot.objects.filter(start_datetime__gte=self.start_datetime, start_datetime__lte=self.end_datetime, start_time__exact=self.start_time).exclude(status__exact="Open")
			#Save a list of unavailable slots into context for the template so we can notify the user of them.
			self.extra_context = {'unavailable_slots' : unavailable_slots}

	def get_template(self, step):
		return 'forms/addlesson.html'

	def done(self, request, form_list):
		#Add a new Lesson for each selected Lesson Slot.
		for slot in form_list[1].cleaned_data['lessonslots']:
			if slot:
				new_lesson = Lesson()
				new_lesson.lesson_type = form_list[2].cleaned_data['lesson_type']
				new_lesson.save()
				new_lesson.students = form_list[2].cleaned_data['students']
				new_lesson.status = form_list[2].cleaned_data['status']
				new_lesson.save()

				#Update the current Lesson Slot with the new Lesson's ID and change Status
				slot.lesson_id = new_lesson.id
				slot.status = 'Booked'
				slot.save()

		return HttpResponseRedirect(reverse('view_season', args=[slot.season_id]))
	
class LessonEditForm(ModelForm):
	class Meta:
		model = Lesson
	