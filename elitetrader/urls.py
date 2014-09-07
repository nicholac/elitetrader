from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

#
'''
urlpatterns = patterns('',
    url(r'^elitetrader/$', views.blos, name='index'),
'''


urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'trader.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),
)
