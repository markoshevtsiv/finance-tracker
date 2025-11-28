import json

from django.contrib import messages

from dateutil.parser import parse

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, authenticate, logout
from django.db.models import Sum, Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView, TemplateView
from .forms import CategoryForm, TransactionForm, BudgetForm, CategoryBudgetForm, CSVImportForm, LoginForm, RegisterForm
from .models import Category, Transaction, MonthBudget, CategoryBudget
import csv

from django.db.models.functions import TruncMonth


# Create your views here.

#Transactions
class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction_form.html'
    success_url = reverse_lazy('transaction_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction_form.html'
    success_url = reverse_lazy('transaction_list')



class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = 'transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')

class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transaction_list.html'
    context_object_name = 'transactions'
    ordering = ['-date']
    paginate_by = 5


    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        search_query = self.request.GET.get('search')
        category_filter = self.request.GET.get('filter')


        if category_filter == 'Income':
            queryset = queryset.filter(category__type='Income')
        elif category_filter == 'Expense':
            queryset = queryset.filter(category__type='Expense')
        elif category_filter == 'all' or category_filter is None:
            queryset = queryset.all()

        if search_query:
            queryset = queryset.filter(
                Q(category__name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(amount__icontains=search_query)
            )

        return queryset

#Category
class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'category_form.html'
    success_url = reverse_lazy('category_list')

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        category_filter = self.request.GET.get('filter')
        search_query = self.request.GET.get('search')

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(type__icontains=search_query)
            )


        if category_filter == 'Income':
            queryset = queryset.filter(type='Income')
        elif category_filter == 'Expense':
            queryset = queryset.filter(type='Expense')
        elif category_filter == 'all' or category_filter is None:
            queryset = queryset.all()
        return queryset



#Budget(month)
class BudgetCreateView(LoginRequiredMixin, CreateView):
    model = MonthBudget
    form_class = BudgetForm
    template_name = 'budget_form.html'
    success_url = reverse_lazy('budget_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        month_budget = self.object

        Category.objects.filter(user__isnull=True).update(user=self.request.user)

        for category in Category.objects.filter(user=self.request.user, type='Expense'):
            CategoryBudget.objects.get_or_create(
                category=category,
                month=month_budget.month_budget,
                user=self.request.user,
                defaults={'amount': 0}
            )

        return response

class BudgetListView(LoginRequiredMixin, ListView):
    model = MonthBudget
    template_name = 'budget_list.html'
    context_object_name = 'budgets'
    paginate_by = 5

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user).order_by('-month_budget')

    @staticmethod
    def get_expenses_for_month(month_date):
        year = month_date.year
        month = month_date.month

        expenses = Transaction.objects.filter(
            category__type='Expense',
            date__year=year,
            date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0

        return expenses

    @staticmethod
    def get_incomes_for_month(month_date):
        year = month_date.year
        month = month_date.month

        incomes = Transaction.objects.filter(
            category__type='Income',
            date__year=year,
            date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0

        return incomes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        budgets = context['budgets']
        for budget in budgets:
            remaining_budget = budget.amount - self.get_expenses_for_month(budget.month_budget)
            income = self.get_incomes_for_month(budget.month_budget)
            expenses = self.get_expenses_for_month(budget.month_budget)
            progress = (self.get_expenses_for_month(budget.month_budget)/ budget.amount) * 100


            budget.remaining = remaining_budget
            budget.expenses = float(expenses)
            budget.income = income
            budget.progress = progress
            budget.exceeded = expenses > budget.amount


        latest_budget = MonthBudget.objects.filter(user=self.request.user).order_by('month_budget').last()
        if latest_budget:
            expenses = self.get_expenses_for_month(latest_budget.month_budget)
            income = self.get_incomes_for_month(latest_budget.month_budget)
            remaining = latest_budget.amount - expenses
            progress = (expenses / latest_budget.amount) * 100 if latest_budget.amount else 0

            latest_budget.expenses = expenses
            latest_budget.income = income
            latest_budget.remaining = remaining
            latest_budget.progress = progress
            latest_budget.exceeded = expenses > latest_budget.amount


            context['latest_budget'] = latest_budget

        return context



class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = MonthBudget
    form_class = BudgetForm
    template_name = 'budget_form.html'
    success_url = reverse_lazy('budget_list')

class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    model = MonthBudget
    template_name = 'budget_confirm_delete.html'
    success_url = reverse_lazy('budget_list')

#BudgetCategory


# class CategoryBudgetCreateView(CreateView):
#     model = CategoryBudget
#     form_class = CategoryBudgetForm
#     template_name = 'category_budget_form.html'
#     success_url = reverse_lazy('category_budget_list')


class CategoryBudgetListView(LoginRequiredMixin, ListView):
    model = CategoryBudget
    template_name = 'category_budget_list.html'
    context_object_name = 'category_budgets'

    @staticmethod
    def get_spent(category_budget):
        transactions = Transaction.objects.filter(
            user=category_budget.user,
            category=category_budget.category,
            date__year=category_budget.month.year,
            date__month=category_budget.month.month,
        ).aggregate(total=Sum('amount'))['total'] or 0

        return transactions


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_budgets = context['category_budgets']

        for category_budget in category_budgets:
            spent = self.get_spent(category_budget)
            category_budget.spent = spent
            category_budget.remaining = category_budget.amount - spent
            if category_budget.amount > 0:
                category_budget.progress = (spent / category_budget.amount) * 100
            else:
                category_budget.progress = 0

        months = CategoryBudget.objects.values_list('month', flat=True).distinct()

        context["available_months"] = sorted({ m for m in months })

        return context

    def get_queryset(self):
        month_param = self.request.GET.get('month')

        base_qs = CategoryBudget.objects.filter(user=self.request.user)

        if month_param:
            year, month = month_param.split('-')
            return base_qs.filter(
                month__year=int(year),
                month__month=int(month)
            )

        first_budget = base_qs.order_by('month').first()

        if not first_budget:
            return base_qs.none()

        return base_qs.filter(
            month__year=first_budget.month.year,
            month__month=first_budget.month.month
        )


class CategoryBudgetUpdateView(LoginRequiredMixin, UpdateView):
    model = CategoryBudget
    form_class = CategoryBudgetForm
    template_name = "category_budget_form.html"
    success_url = reverse_lazy('category_budget_list')

class CategoryBudgetDeleteView(LoginRequiredMixin, DeleteView):
    model = CategoryBudget
    template_name = 'category_confirm_delete.html'
    success_url = reverse_lazy('category_budget_list')




# Home page
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        selected_month = self.request.GET.get('month')
        user = self.request.user

        if selected_month:
            year, month = map(int, selected_month.split('-'))
        else:
            today = timezone.now()
            month = today.month
            year = today.year

        expenses = Transaction.objects.filter(
            user=user,
            category__type = 'Expense',
            date__year=year,
            date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0

        incomes = Transaction.objects.filter(
            user=user,
            category__type = 'Income',
            date__year=year,
            date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0

        balance = incomes - expenses

        context['total_categories'] = Category.objects.filter(user=user).count()
        context['total_transactions'] = Transaction.objects.filter(user=user).count()

        categories = Category.objects.filter(user=user, type='Expense')
        chart_labels = []
        chart_values = []
        chart_colors = []


        for category in categories:
            total = Transaction.objects.filter(
                user=user,
                category=category,
                date__year=year,
                date__month=month
            ).aggregate(total=Sum('amount'))['total'] or 0

            if total > 0:
                chart_values.append(float(total))
                chart_labels.append(category.name)
                chart_colors.append(category.color)

        available_months = (
            Transaction.objects.filter(user=user)
            .annotate(month=TruncMonth('date'))
            .values_list('month', flat=True)
            .distinct()
            .order_by('-month')
        )

        last_transactions = Transaction.objects.filter(user=user).order_by('-date')[:5]

        try:
            month_budget = MonthBudget.objects.get(
                user=user,
                month_budget__year=year,
                month_budget__month=month
            )
            monthly_budget = month_budget.amount

        except MonthBudget.DoesNotExist:
            monthly_budget = None

        context['expenses'] = float(expenses)
        context['incomes'] = float(incomes)
        context['balance'] = float(balance)
        context["chart_labels"] = json.dumps(list(chart_labels))
        context["chart_values"] = json.dumps(list(chart_values))
        context["chart_colors"] = json.dumps(list(chart_colors))
        context['available_months'] = available_months
        context['last_transactions'] = last_transactions
        context['monthly_budget'] = monthly_budget


        if monthly_budget is not None:
            context['monthly_remaining'] = monthly_budget - expenses


        return context




# CSV Import
@login_required(login_url='/accounts/login/')
def import_csv(request):

    Category.objects.filter(user__isnull=True).update(user=request.user)

    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                csv_file = request.FILES['file']
                decoder = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoder)

                for row in reader:
                    name = row['category'].strip()
                    csv_type = row['type'].strip()
                    csv_color = row['color'].strip()
                    csv_date = row['date'].strip()
                    csv_amount = Decimal(row['amount'])
                    csv_description = row.get('description', '').strip()


                    category_obj, created = Category.objects.get_or_create(
                        name=name,
                        user=request.user
                    )


                    category_obj.type = csv_type
                    category_obj.color = csv_color
                    category_obj.save()

                    Transaction.objects.create(
                        date=parse(csv_date).date(),
                        amount=csv_amount,
                        category=category_obj,
                        description=csv_description,
                        user=request.user
                    )
            except:
                messages.error(request, 'Error importing CSV. Make sure your file match the structure')

            return redirect('transaction_list')

    else:
        form = CSVImportForm()

    return render(request, 'import_csv.html', {'form': form})



#Login and Register

def login_view(request):
    if request.method == 'GET':
        login_form = LoginForm()
        return render(request, 'login.html', {'form': login_form})
    elif request.method == 'POST':
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is None:
                messages.error(request, 'Invalid username or password.')
            else:
                login(request, user)
                # messages.success(request, 'You are now logged in!')
                return redirect('home')

            return render(request, 'login.html', {'form': login_form})


def register_view(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.save()
            login(request, username)
            messages.success(request, 'You are now registered!')

            return redirect('home')

        return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Now you are logged out!')
    return redirect('home')