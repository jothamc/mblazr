# edgarapp/admin.py
from django.contrib import admin
from .models import Company, Filing


class CompanyAdmin(admin.ModelAdmin):
    list_display = ("cik", "ticker", "name")


class FilingAdmin(admin.ModelAdmin):
    list_display = ("cik", "name", "filingtype", "filingdate", "filingpath")


admin.site.register(Company, CompanyAdmin)
admin.site.register(Filing, FilingAdmin)