from django.conf.urls.defaults import *
from django.contrib import admin


urlpatterns = patterns('django.views.generic.simple',
		       
		       (r'^$', 'direct_to_template', {'template': 'main2col.html'}), #Catch root url to homepage
		       (r'^manage/$', 'redirect_to', {'url': '/schedule/manage/'}),
)

urlpatterns += patterns('',
		       # Example:
		       # (r'^stswim/', include('stswim.foo.urls')),
		   
		       #urls.py includes
		       (r'^accounts/', include('stswim.accounts.urls')),
		       (r'^schedule/', include('stswim.schedule.urls')),
		       
		       #Pages app admin urls
		       (r'^admin/pages/page/$', 'stswim.pages.admin_views.list_pages'),
		       (r'^admin/pages/page/(?P<hnode_id>\d+)/up/$', 'stswim.pages.admin_views.up'),
		       (r'^admin/pages/page/(?P<hnode_id>\d+)/down/$', 'stswim.pages.admin_views.down'),
		       
		       # Built-In Admin
		       (r'^admin/(.*)', admin.site.root),

		       # Handle static files
		       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/stephen/Projects/stswim/media'}),
		       
		       #content pages
		       #(r'^(?P<page_slug>\w+)/$', 'pages.views.details'),
		       (r'^(?P<full_slug>(.*))/$', 'stswim.pages.views.details'),
)


