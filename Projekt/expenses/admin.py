from django.contrib import admin
from .models import Category, Expense, Budget

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'user']
    list_filter = ['user']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'date', 'category', 'user']
    list_filter = ['category', 'date', 'user']
    search_fields = ['title', 'description']

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'monthly_limit', 'month', 'year', 'user']
    list_filter = ['user', 'year', 'month']
