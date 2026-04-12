

from django.contrib import admin
from .models import Criminal, Police, Incidents

admin.site.register(Criminal)
admin.site.register(Police)
admin.site.register(Incidents)

admin.site.site_header = "LVPD Central Database"
admin.site.site_title = "LVPD Admin Portal"
admin.site.index_title = "Official Surveillance & Records"