from django.contrib import admin
from .models import User, LoanApplication

class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'f1_income', 'f2_amount', 'f3_duration', 'f4_credit_score', 'prediction_result', 'created_at')
    list_filter = ('prediction_result', 'created_at')
    search_fields = ('user__username', 'prediction_result')
    ordering = ('-created_at',)

# Sajili model kwa njia ya kawaida ya Django chini kabisa
admin.site.register(LoanApplication, LoanApplicationAdmin)