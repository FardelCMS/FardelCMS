from .site import ModelAdmin, site
from fardel.core.auth import models


class UserAdmin(ModelAdmin):
    pass


class GroupAdmin(ModelAdmin):
    pass


site.register(models.User, UserAdmin)
site.register(models.Group, GroupAdmin)
