from django.contrib import admin
from sign.models import Event, Guest


class EventAdmin(admin.ModelAdmin):
    # 在页面中显示列表中的字段
    list_display = ["id", "name", "status", "address", "start_time"]
    search_fields = ["name"]  # 搜索栏（以name为值搜索）
    list_filter = ["status"]  # 过滤器（以status的值作为条件过滤）


class GuestAdmin(admin.ModelAdmin):
    # 在页面中显示列表中的字段
    list_display = ["realname", "phone", "email", "sign", "create_time", "event"]
    search_fields = ["realname", "phone"]  # 搜索栏（以realname或者phone为值搜索）
    list_filter = ["sign"]  # 过滤器（以sign的值作为条件过滤）


admin.site.register(Event, EventAdmin)
admin.site.register(Guest, GuestAdmin)
