from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from decimal import Decimal

TYPE_CHOICE = [
    ('Income', 'Income'),
    ('Expense', 'Expense')]
TYPE_CHOICE2 = [
    ('#FF0000', 'Red'),
    ('#0000FF', 'Blue'),
    ('#00FF00', 'Green'),
    ('#FFFF00', 'Yellow'),
    ('#800080', 'Purple'),
    ('#FFA500', 'Orange'),
    ('#FFC0CB', 'Pink'),
    ('#008080', 'Teal'),
    ('#A52A2A', 'Brown'),
    ('#808080', 'Gray'),
    ('#000000', 'Black'),
    ('#00FFFF', 'Cyan'),
]
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices= TYPE_CHOICE)
    color = models.CharField(max_length=7, choices= TYPE_CHOICE2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.name

class Transaction(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date = models.DateField()
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.category} - {self.amount}'

class MonthBudget(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month_budget = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "month_budget"],
                name="unique_user_month_budget",
            )
        ]

    def __str__(self):
        return f'Budget -{self.amount} - {self.month_budget}'

class CategoryBudget(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('category', 'month'),)

    def __str__(self):
        return f'Budget -{self.amount} - {self.month}'