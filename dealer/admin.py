from django.contrib import admin
from .models import DealerProfile


@admin.register(DealerProfile)
class DealerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'phone', 'is_dealer', 'created_at')
    list_filter = ('is_dealer', 'created_at')
    search_fields = ('user__username', 'business_name', 'phone')
    readonly_fields = ('created_at',)
