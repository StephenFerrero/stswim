from django.conf import settings
from django import newforms as forms
from django.contrib.formtools.wizard import FormWizard
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.newforms import ModelForm
from stswim.schedule.models import SEX_CHOICES, LESSON_TYPES, LESSON_STATUS, Student, Season, LessonSlot, Lesson
from dateutil import rrule
from datetime import timedelta

class PersonSearchForm(forms.Form):
	query = forms.CharField(
		label='Enter a name to search for',
		widget = forms.TextInput(attrs={'size': 20})
	)

class StudentAddForm(forms.Form):

	def __init__(self, household_id, *args, **kwargs):
		super(StudentAddForm, self).__init__(*args, **kwargs)
		
		self.household_id = household_id

	first_name = forms.CharField(max_length=40)
	last_name = forms.CharField(max_length=40)
	birth_date = forms.DateField()
	sex = forms.ChoiceField(choices=SEX_CHOICES)
	has_liabilityform = forms.BooleanField(label="Has Liability Form", required=False)
		

	def save(self):
		new_student = Student()
		new_student.household_id = self.household_id
		new_student.first_name = self.cleaned_data['first_name']
		new_student.last_name = self.cleaned_data['last_name']
		new_student.sex = self.cleaned_data['sex']
		new_student.birth_date = self.cleaned_data['birth_date']
		new_student.has_liabilityform = self.cleaned_data['has_liabilityform']
		new_student.save()
		
		return new_student.household_id

class StudentEditForm(ModelForm):
	class Meta:
		model = Student

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

#Need to validate against existing  lessonslots		
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
	start_time = forms.DateTimeField(input_formats = settings.TIME_INPUT_FORMATS, help_text='All lessonslots are 30 min.')

	def save(self):
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

		days = rrule.rrule(rrule.WEEKLY, wkst=rrule.SU, byweekday=selected_weekdays, dtstart=self.cleaned_data['start_date'], until=self.cleaned_data['end_date'])
	
		for d in days:
			#Check for existing LessonSlots, if they exist do nothing.
			if not LessonSlot.objects.filter(season__exact = self.cleaned_data['season'].id,
										 date__exact = d, 
										 start_time__exact = self.cleaned_data['start_time']):
				new_lessonSlot = LessonSlot()
				new_lessonSlot.season_id = self.cleaned_data['season'].id
				new_lessonSlot.date = d
				new_lessonSlot.start_time = self.cleaned_data['start_time']
				new_lessonSlot.end_time = new_lessonSlot.start_time + timedelta(minutes=30)
				new_lessonSlot.weekday = d.weekday()
				new_lessonSlot.status = 'Open'
				new_lessonSlot.save()

		return self.cleaned_data['season'].id

#AddLessonWizard Step 0
class AddLessonForm1(forms.Form):
	season = forms.ModelChoiceField(Season.objects.all())
	start_date = forms.DateField()
	end_date = forms.DateField()
	start_time = forms.TimeField(input_formats = settings.TIME_INPUT_FORMATS)
	
	#Override form clean method to check if there are any available lessons before continuing.
	def clean(self):
		available_slots = LessonSlot.objects.filter(season__exact = self.cleaned_data['season'], status__exact = 'Open',
							    date__gte = self.cleaned_data['start_date'], 
							    date__lte = self.cleaned_data['end_date'], 
							    start_time__exact = self.cleaned_data['start_time'],  
							    weekday__exact = self.cleaned_data['start_date'].weekday())
		if available_slots:
			return self.cleaned_data
		else: 
			raise forms.ValidationError('There are no available lessons within the requested criteria.')

			#AddLessonWizard Step 1
class AddLessonForm2(forms.Form):
	#Dynamically create a boolean field for each Lesson Slot matching the criteria from Step 0
	def __init__(self, *args, **kwargs):

		start_date = kwargs['start_date']
		end_date = kwargs['end_date']
		start_time = kwargs['start_time']
		weekday = kwargs['start_date'].weekday()
		del kwargs['start_date']
		del kwargs['end_date']
		del kwargs['start_time']

		super(AddLessonForm2, self).__init__(*args, **kwargs)

		self.fields['lessonslots'] = forms.ModelMultipleChoiceField(LessonSlot.objects.filter(status__exact='Open', date__gte=start_date, date__lte=end_date, start_time__exact=start_time, weekday__exact=weekday), 
									    widget = forms.CheckboxSelectMultiple,
									    label="Available Lessonslots:")

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
						    start_time=self.start_time,)

		return self.form_list[step](data, prefix=self.prefix_for_step(step), initial=self.initial.get(step, None))

	def process_step(self, request, form, step):
		#Save data from Step 0 to be used in processing Step 1
		if step == 0:
			form.is_valid()
			self.start_date = form.cleaned_data['start_date']
			self.end_date = form.cleaned_data['end_date']
			self.start_time = form.cleaned_data['start_time']

			unavailable_slots = LessonSlot.objects.filter(date__gte=self.start_date, date__lte=self.end_date, start_time__exact=self.start_time, weekday__exact=self.start_date.weekday()).exclude(status__exact="Open")
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
	