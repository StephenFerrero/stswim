from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
import random

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
ALLCHAR = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%&"

def random_string(length, variable=False, charset=LETTERS):
	if variable:
		length = random.randrange(1, length+1)
	return ''.join([random.choice(charset) for x in xrange(length)])

def generate_id(first_name=None, last_name=None):
	"""
	Create a unique user id given a first and last name.
	First, we try simple concatenation of first and last name.
	If that doesn't work, we add random numbers to the name
	Taken from satchmo.
	"""
	valid_id = False
	test_name = first_name + last_name
	while valid_id is False:
		try:
			User.objects.get(username=test_name)
		except User.DoesNotExist:
			valid_id = True
		else:
			test_name = first_name + last_name + "_" + random_string(7, True)
	return(test_name)

def auto_render(func):
    """Decorator that put automaticaly the template path in the context dictionary
    and call the render_to_response shortcut"""
    def _dec(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, HttpResponse) or isinstance(response, HttpResponseRedirect):
            return response
        (template_name, context) = response
        context['template_name'] = template_name
        return render_to_response(template_name, context, context_instance=RequestContext(request))
    return _dec