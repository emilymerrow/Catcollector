from django.contrib import admin

# Register your models here.
from .models import Cat, Feeding, Toy, Photo

# Add our Cat model to the admin site, so we can perform
# CRUD operations on it!
admin.site.register(Cat)
admin.site.register(Feeding)
admin.site.register(Toy)
admin.site.register(Photo)