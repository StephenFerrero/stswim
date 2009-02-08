from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required
from forms import *

# Parent Add Form
@staff_member_required
def addparent(request, household_id=None):
	if request.method == 'POST':
		form = ParentAddForm(household_id, request.POST)
		form_instructions = ''
		if form.is_valid():
			parent = form.save()
			if not household_id:
				household_id = parent.household_id
				
			return HttpResponseRedirect(reverse('view_household', args=[household_id]))
	else:
		form = ParentAddForm()
		if not household_id:
			form_instructions = 'This form is for adding a new parent to a NEW household. If this parent should be added to an existing household please goto that household and use the add parent link there'
		else:
			form_instructions = 'This form is for adding a parent to an EXISTING household. If you are trying to create a new household use the Add Parent link in the Tools section'
	
	return render_to_response("schedule/manageform.html", {'form' : form, 'form_title' : 'Add Parent', 'form_instructions' : form_instructions}, 
				  context_instance=RequestContext(request))