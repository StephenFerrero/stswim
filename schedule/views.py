from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from stswim.schedule.models import Season, Student, LessonSlot

from datetime import date
	
	
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
	
	todayslessonslots = LessonSlot.objects.filter(start_datetime__exact = display_date)
	
	return render_to_response("schedule/dayview.html", 
								{'display_date' : display_date, 'todayslessonslots' : todayslessonslots, 'season' : season},
								context_instance=RequestContext(request))

#permit only members of same household to view student								
def viewstudent(request, student_id):
	student = Student.objects.get(id = student_id)
	
	return render_to_response("schedule/student_detail.htm")