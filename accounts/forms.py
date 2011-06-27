from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from stswim.utils import generate_id, random_string
from stswim.schedule.models import Household, Parent
from stswim.accounts.models import RegistrationProfile
from datetime import date
from django.core.mail import send_mail
from django.template.loader import render_to_string

class ParentAddForm(forms.Form):
	"""Form used by admins to add a parent object and corresponding user account"""
	
	def __init__(self, household_id=None, *args, **kwargs):
		#override __init__ to allow for additional argument 'household_id'
		super(ParentAddForm, self).__init__(*args, **kwargs)
		
		self.household_id = household_id
		
	first_name = forms.CharField(max_length=30)
	last_name = forms.CharField(max_length=30)
	email = forms.EmailField(required=False)
	#email2 = forms.EmailField(label="Email (again)")
	phone_number = forms.CharField(max_length=30)
	address = forms.CharField(max_length=30)
	address2 = forms.CharField(max_length=30, required=False)
	city = forms.CharField(max_length=30)
	state = forms.CharField(max_length=2)
	zip_code = forms.CharField(max_length=30)
	has_registrationform = forms.BooleanField(label="Has Registration Form", required=False)
	
	def clean_email(self):		
		email = self.cleaned_data.get('email', None)
		if email and User.objects.filter(email=email).count() > 0:
			raise forms.ValidationError('That email address is already in use.')
			
		return self.data['email']
		
	def clean(self, *args, **kwargs):
		self.clean_email()
		return super(ParentAddForm, self).clean(*args, **kwargs)
		
	def save(self):
		"""Create a new parent, household and a new user if email address is provided. Returns the new parent."""
		
		data = self.cleaned_data
		email = data['email']
		first_name = data['first_name']
		last_name = data['last_name']
		phone_number = data['phone_number']
		address = data['address']
		address2 = data['address2']
		city = data['city']
		state = data['state']
		zip_code = data['zip_code']
		has_registrationform = data['has_registrationform']
		
		if email:
			username = email
			password = random_string(7, variable=False, charset='ALLCHAR')
			
			new_user = User.objects.create_user(username, email, password)
			new_user.first_name = first_name
			new_user.last_name = last_name
			new_user.save()
		
		#check if we are providing an existing household, if not create a new one, if so then attach new parent to that household.
		if not self.household_id:
			household = Household()
			household.creation_date = date.today()
			household.save()
		else:
			household = Household.objects.get(id=self.household_id)
		
		new_parent = Parent()
		if email:
		new_parent.user_id = new_user.id
		new_parent.household = household
		new_parent.first_name = first_name
		new_parent.last_name = last_name
		new_parent.email = email
		new_parent.phone_number = phone_number
		new_parent.address = address
		new_parent.address2 = address2
		new_parent.city = city
		new_parent.state = state
		new_parent.zip_code = zip_code
		new_parent.has_registrationform = has_registrationform
		new_parent.save()
		
		return new_parent

class ParentEditForm(ModelForm):
	class Meta:
		model = Parent

class ParentRegistrationForm(forms.Form):
	"""The basic Parent registration form."""
	email = forms.EmailField(label="Parent's Email", help_text='A valid e-mail address, please.')
	email2 = forms.EmailField(label="Confirm Email")
	password = forms.CharField(widget=forms.PasswordInput(render_value=False))
	password2 = forms.CharField(widget=forms.PasswordInput(render_value=False), label="Confirm Password")
	first_name = forms.CharField(max_length=30, label="Parent's First Name")
	last_name = forms.CharField(max_length=30, label="Parent's Last Name")
	phone_number = forms.CharField(max_length=30)
	address = forms.CharField(max_length=30)
	address2 = forms.CharField(max_length=30, required=False)
	city = forms.CharField(max_length=30)
	state = forms.CharField(max_length=2)
	zip_code = forms.CharField(max_length=30)
			
	def clean_email(self):
		"""Verify correct email address was entered and
		Prevent duplicate accounts by checking email address against existing users"""
		if self.data['email'] != self.data['email2']:
			raise forms.ValidationError("Email addresses do not match.")
			
		email = self.cleaned_data.get('email', None)
		if email and User.objects.filter(email=email).count() > 0:
			raise forms.ValidationError('That email address is already in use. Please use the password recovery option for existing parents.')
			
		return self.data['email']
		
	def clean_password(self):
		"""Make sure that the two passwords entered match"""
		if self.data['password'] != self.data['password2']:
			raise forms.ValidationError("Passwords do not match.")
		return self.data['password']
		
	def clean(self, *args, **kwargs):
		self.clean_email()
		self.clean_password()
		return super(ParentRegistrationForm, self).clean(*args, **kwargs)
		
	def save(self):
		"""Create a new user and parent. Returns the new user."""
		data = self.cleaned_data
		password = data['password']
		email = data['email']
		first_name = data['first_name']
		last_name = data['last_name']
		phone_number = data['phone_number']
		address = data['address']
		address2 = data['address2']
		city = data['city']
		state = data['state']
		zip_code = data['zip_code']
		
		username = generate_id(first_name, last_name)
		
		#new_user = RegistrationProfile.objects.create_inactive_user(username, password, email, send_email=True)
		new_user = User.objects.create_user(username, email, password)
					
		new_user.first_name = first_name
		new_user.last_name = last_name
		new_user.save()
		#new_user.groups.add(2)
		
		new_household = Household()
		new_household.creation_date = date.today()
		new_household.save()
		
		new_parent = Parent()
		new_parent.user_id = new_user.id
		new_parent.household = new_household
		new_parent.first_name = first_name
		new_parent.last_name = last_name
		new_parent.email = email
		new_parent.phone_number = phone_number
		new_parent.address = address
		new_parent.address2 = address2
		new_parent.city = city
		new_parent.state = state
		new_parent.zip_code = zip_code
		new_parent.save()
		
		subject = 'Seaturtle Swim School Online Registration'
		
		message = render_to_string('registration/new_account_confirmation.txt',
								{ 'email': email,
									'password': password,
									})
		
		send_mail(subject, message, 'website@seaturtleswim.com', [new_user.email])
		
		return new_user