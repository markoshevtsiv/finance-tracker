from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Category, MonthBudget, Transaction, CategoryBudget


class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        if user:
            self.fields["category"].queryset = Category.objects.filter(user=user)
        else:
            self.fields["category"].queryset = Category.objects.none()

    class Meta:
        model = Transaction
        fields = ['category', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Category
        fields = ['name', 'type', 'color']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'})
        }



class BudgetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_month_budget(self):
        date = self.cleaned_data['month_budget']
        return date.replace(day=1)


    class Meta:
        model = MonthBudget
        fields = ['amount', 'month_budget']
        widgets = {
            'month_budget': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }



class CategoryBudgetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = CategoryBudget
        fields = ['amount']


class CSVImportForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))


class LoginForm(forms.Form):
    username = forms.CharField(max_length=25)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class RegisterForm(UserCreationForm):
    model = User
    fields = ['username', 'email', 'password1', 'password2']
