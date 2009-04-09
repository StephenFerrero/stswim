# Template Tag
from datetime import date, datetime, timedelta
from stswim.schedule.models import *
import calendar

from django import template

register = template.Library()
#
# TODO
#  - Write logic to prevent next/previous month buttons from breaking. (going out of range 1-12, going out of range of season)
#  - Clean up context variables to template
#  - Cleaner way to find deltas?
#	
def season_month_cal(context):
	season = context['season']
	display_month = context['display_month']
	user = context['user']
	perms = context['perms']
	season = Season.objects.get(id = season.id)
	year = season.start_date.year
	today = date.today()
	if not display_month:
		month = date.today().month
	else:
		month = int(display_month)
	first_weekday_of_month, month_days = calendar.monthrange(year, month)
	first_day_of_season = season.start_date
	first_day_of_month = date(year, month, 1)
	last_day_of_month = date(year, month, month_days)
	
	if first_day_of_month.weekday()+1 == 7:
		first_day_of_calendar_delta = 0
	else:
		first_day_of_calendar_delta = first_day_of_month.weekday()+1
		
	first_day_of_calendar = first_day_of_month - timedelta(first_day_of_calendar_delta)
	
	if 7 - last_day_of_month.weekday() == 1:
		last_day_of_calendar_delta = 7
	else:
		last_day_of_calendar_delta = 7 - last_day_of_month.weekday()
		
	last_day_of_calendar = last_day_of_month + timedelta(last_day_of_calendar_delta)
	lesson_slot_list = LessonSlot.objects.all()
	
	month_cal = []
	week = []
	week_headers = []
	
	i = 0
	day = first_day_of_calendar
	while day <= last_day_of_calendar:
		if i < 7:
			week_headers.append(day)
		cal_day = {}
		cal_day['day'] = day
		cal_day['lessons'] = False
		cal_day_lessons = []
		for lesson in lesson_slot_list:
			if day == lesson.start_date.date():
				cal_day_lessons.append(lesson)
		cal_day['lessons'] = cal_day_lessons
		week.append(cal_day)
		if day.weekday() == 5:
			month_cal.append(week)
			week = []
		i += 1
		day += timedelta(1)
		
	return{'calendar': month_cal, 
			'user': user,
			'perms': perms,
			'headers': week_headers, 
			'season': season, 
			'current_month': first_day_of_month.strftime("%B"),
			'today' : today ,
			'next_month': first_day_of_month.month+1, 
			'prev_month': first_day_of_month.month-1}
	
register.inclusion_tag('schedule/month_cal.html', takes_context=True)(season_month_cal)

def month_cal(year=date.today().year, month=date.today().month, day=date.today().day):
	first_day_of_month = date(year, month, 1)
	last_day_of_month = get_last_day_of_month(year, month)
	first_day_of_week = date(year, month, day)
	first_day_of_calendar = first_day_of_month - timedelta(first_day_of_month.weekday()+1)
	last_day_of_calendar = first_day_of_calendar + timedelta(7 - first_day_of_calendar.weekday())
	
	month_cal = []
	week = []
	week_headers = []
	
	i = 0
	day = first_day_of_calendar
	while i <= 7:
		if i < 7:
			week_headers.append(day)
		cal_day = {}
		cal_day['day'] = day
		if day.month == month:
			cal_day['in_month'] = True
		else:
			cal_day['in_month'] = False
		week.append(cal_day)
		if day.weekday() == 5:
			month_cal.append(week)
			week = []
		i += 1
		day += timedelta(1)
		
	return{'calendar': month_cal, 'headers': week_headers}
	
register.inclusion_tag('schedule/month_cal.htm')(month_cal)