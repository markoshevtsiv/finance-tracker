from django.contrib.auth.views import LogoutView
from django.urls import path

from .models import CategoryBudget
from .views import (
    TransactionListView, TransactionCreateView, TransactionUpdateView, TransactionDeleteView,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    BudgetListView, BudgetCreateView, BudgetUpdateView, BudgetDeleteView, HomeView, CategoryBudgetListView,
    CategoryBudgetUpdateView, import_csv, login_view, register_view, logout_view
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    # Transactions
    path('transactions/', TransactionListView.as_view(), name='transaction_list'),
    path('transactions/create/', TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/<int:pk>/update/', TransactionUpdateView.as_view(), name='transaction_update'),
    path('transactions/<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction_delete'),

    # Categories
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),

    # Budgets
    path('budgets/', BudgetListView.as_view(), name='budget_list'),
    path('budgets/create/', BudgetCreateView.as_view(), name='budget_create'),
    path('budgets/<int:pk>/update/', BudgetUpdateView.as_view(), name='budget_update'),
    path('budgets/<int:pk>/delete/', BudgetDeleteView.as_view(), name='budget_delete'),


    #CategoryBudget
    path('category_budgets/', CategoryBudgetListView.as_view(), name='category_budget_list'),
    path('category_budgets/update/<int:pk>/', CategoryBudgetUpdateView.as_view(), name='category_budget_update'),

    #CSVImport
    path('transactions/import', import_csv, name='import_csv'),

    #Login, Register, Logout
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
]

