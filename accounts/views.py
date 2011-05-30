from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from stswim.accounts.forms import *

# Create your views here.

def activate(request, activation_key, template_name='registration/activate.html'):
    """
    Activates a ``User``'s account, if their key is valid and hasn't
    expired.
    
    By default, uses the template ``registration/activate.html``; to
    change this, pass the name of a template as the keyword argument
    ``template_name``.
    
    **Context:**
    
    account
        The ``User`` object corresponding to the account, if the
        activation was successful. ``False`` if the activation was not
        successful.
    
    expiration_days
        The number of days for which activation keys stay valid after
        registration.
    
    **Template:**
    
    registration/activate.html or ``template_name`` keyword argument.
    
    """
    activation_key = activation_key.lower() # Normalize before trying anything with it.
    account = RegistrationProfile.objects.activate_user(activation_key)
    return render_to_response(template_name,
                              { 'account': account,
                                'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS },
                              context_instance=RequestContext(request))
							  

def registerparent(request):
	"""Registration form used by parents to register themselves"""
	if request.method == 'POST':
		form = ParentRegistrationForm(request.POST)
		if form.is_valid():
			user = form.save()
			email = form.cleaned_data['email']
			return render_to_response("registration/registration_success.html", {'email' : email}, context_instance=RequestContext(request))
	else:
		form = ParentRegistrationForm()	
	return render_to_response("schedule/parent_registration_form.html", {'form' : form}, context_instance=RequestContext(request))

def UserProfile(request):
	"""Basic view of any user account's profile."""
	
	
	return render_to_response("registration/profile.html", 
								context_instance=RequestContext(request))