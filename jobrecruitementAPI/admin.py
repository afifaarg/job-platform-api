from django.contrib import admin
from .models import PlatformUser, Education, DesiredJob

admin.site.register(PlatformUser)
admin.site.register(Education)
admin.site.register(DesiredJob)