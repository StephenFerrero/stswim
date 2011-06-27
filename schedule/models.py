from django.forms import ModelForm
from django.db import models
from django.contrib.localflavor.us.models import USStateField, PhoneNumberField
from django.contrib.auth.models import User

SEX_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
)

LESSON_TYPES = (
    ('Private', 'Private'),
    ('Semi-Private', 'Semi-Private'),
    ('Small-Group', 'Small-Group'),
    ('Large-Group', 'Large-Group'),
)

LESSONSLOT_STATUS = (
    ('Open', 'Open'),
    ('Closed', 'Closed'),
    ('Pending', 'Pending'),
    ('Booked', 'Booked'),
)

LESSON_STATUS = (
    ('Booked', 'Booked'),
    ('Open', 'Open'),
    ('Pending', 'Pending'),
    ('Cancelled', 'Cancelled'),
)

EMPLOYEE_STATUS = (
	('Active', 'Active'),
	('Inactive', 'Inactive'),
)

STATUS = (
	('0', 'Inactive'),
	('1', 'Active'),
)

class Household(models.Model):
    creation_date = models.DateField()

    class Meta:
        permissions = (
                ("can_viewhousehold", "Can view households"),
                )

class Parent(models.Model):
    user = models.ForeignKey(User, unique=True, editable=False, blank=True, null=True)
    household = models.ForeignKey(Household, editable=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(blank=True, null=True)
    phone_number = PhoneNumberField()
    address = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    state = USStateField()
    zip_code = models.CharField(max_length=5)
    has_registrationform = models.BooleanField("Has registration form", blank=True)
    
    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)
    
    class Meta:
        ordering = ['last_name']
        permissions = (
                ("can_viewparents", "Can view parents"),
                )
        
class Student(models.Model):
    household = models.ForeignKey(Household, editable=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    birth_date = models.DateField()
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    has_liabilityform = models.BooleanField("Has liability form", blank=True)
    
    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)
    
    class Meta:
        ordering = ['last_name']
        permissions = (
                ("can_viewstudents", "Can view students"),
                )

class Employee(models.Model):
    status =  models.CharField(choices=EMPLOYEE_STATUS, default='Active', max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    birth_date = models.DateField()
    phone_number = PhoneNumberField()
    address = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    state = USStateField()
    zip_code = models.CharField(max_length=5)
    
    def __unicode__(self):
        return '%s' % (self.first_name)

class Season(models.Model):
    status = models.CharField(choices=STATUS, max_length=30)
    name = models.CharField(max_length=30)
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __unicode__(self):
        return '%s' % (self.name)
        
    class Meta:
        ordering = ['start_date']
        permissions = (
                ("can_viewfullschedule", "Can view full schedule"),
                )

class Lesson(models.Model):
    lesson_type = models.CharField(choices=LESSON_TYPES, max_length=30)
    students = models.ManyToManyField(Student, blank=True)
    status = models.CharField(choices=LESSON_STATUS, max_length=30)
    
    def __unicode__(self):
        return '%s %s' % (LessonSlot.objects.get(lesson__exact = self).start_datetime, LessonSlot.objects.get(lesson__exact = self).start_time)
    
    class Meta:
        permissions = (
                ("can_booklesson", "Can book lessons"),
                )
    
    def cancel(self):
        lessonslot = self.lessonslot_set.all()[0]
        lessonslot.status = 'Open'
        lessonslot.lesson = None
        lessonslot.save()
        
        self.delete()
    
    def removestudent(self, student):
        self.students.remove(student)
        self.save()

    def addstudent(self, student):
        self.students.add(student)
        self.save()

#Lesson Slots are time slots that lessons fit into. Slots can be open, closed, booked etc...        
class LessonSlot(models.Model):
    season = models.ForeignKey(Season, null=True, blank=True)
    start_datetime = models.DateTimeField()
    start_time = models.TimeField()
    end_datetime = models.DateTimeField()
    end_time = models.TimeField()
    weekday = models.IntegerField()
    lesson = models.ForeignKey(Lesson, null=True, blank=True)
    instructor = models.ForeignKey(Employee, null=True, blank=True)
    status = models.CharField(choices=LESSONSLOT_STATUS, max_length=30)
    
    class Meta:
        ordering = ['start_datetime']
    
    def __unicode__(self):
        return '%s/%s/%s %s' % (self.start_datetime.month, self.start_datetime.day, self.start_datetime.year, self.start_datetime.time())
        
    def close(self):
        self.status = 'Closed'
        self.save()
    
    def open(self):
        self.status = 'Open'
        self.save()
