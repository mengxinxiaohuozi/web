from django.contrib import admin
from .models import LoanRecord

@admin.register(LoanRecord)
class LoanRecordAdmin(admin.ModelAdmin):
    list_display = ('loan_number', 'customer_name', 'loan_amount', 'loan_date', 'status', 'created_at')
    list_filter = ('status', 'loan_date', 'created_at')
    search_fields = ('loan_number', 'customer_name')
    ordering = ('-created_at',)
