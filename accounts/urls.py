"""
URLConf for User registration and authentication
"""

from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, password_change, password_change_done, password_reset, password_reset_done
from stswim.accounts.views import activate

urlpatterns = patterns('',
	url(r'^login/$',  login, name="login"),
	url(r'^logout/$', logout, name="logout"),
	
	# Activation keys get matched by \w+ instead of the more specific
	# [a-fA-F0-9]{40} because a bad activation key should still get to the view;
	# that way it can return a sensible "invalid key" message instead of a
	# confusing 404.
	url(r'^activate/(?P<activation_key>\w+)/$', 'stswim.accounts.views.activate', name='registration_activate'),
	
	url(r'^password/change/$', password_change, name='auth_password_change'),
	url(r'^password/change/done/$', password_change_done, name='auth_password_change_done'),
	url(r'^password/reset/$', password_reset, name='auth_password_reset'),
	url(r'^password/reset/done/$', password_reset_done, name='auth_password_reset_done'),
		
	#(r'^parent/register/$', 'stswim.accounts.views.registerparent'),
	#(r'^employee/register/$', stswim.accounts.views.registeremployee),
	
	(r'^profile/$', 'stswim.accounts.views.UserProfile'),
	
)