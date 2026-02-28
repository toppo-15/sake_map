from django.contrib import admin
from .models import Prefecture, Brewery, Sake, SakeLog

# Register your models here.
admin.site.register(Prefecture)
admin.site.register(Brewery)
admin.site.register(Sake)
admin.site.register(SakeLog)