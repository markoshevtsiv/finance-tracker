from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Transaction, MonthBudget, CategoryBudget


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'color')
    list_filter = ('type', 'color')
    search_fields = ('name',)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'date', 'description')
    list_filter = ('category', 'date')
    search_fields = ('description',)


class BudgetAdmin(admin.ModelAdmin):
    list_display = ('amount', 'month_budget')
    list_filter = ('month_budget',)
    search_fields = ('amount',)

class CategoryBudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'month',)
    list_filter = ('month',)
    search_fields = ('amount',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(MonthBudget, BudgetAdmin)
admin.site.register(CategoryBudget, CategoryBudgetAdmin)
