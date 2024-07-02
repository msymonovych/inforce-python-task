from django.contrib import admin

from restaurant.models import (
    Restaurant,
    Menu,
    MenuItem,
    Vote,
)


admin.site.register(Restaurant)
admin.site.register(Menu)
admin.site.register(MenuItem)
admin.site.register(Vote)
