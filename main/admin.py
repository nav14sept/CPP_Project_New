from django.contrib import admin
from .models import *


# Register your models here.

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Chapter)
admin.site.register(Exercise)
admin.site.register(Solution)
admin.site.register(UserLibrary)
