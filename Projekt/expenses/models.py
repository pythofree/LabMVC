from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#007bff')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def total_spent_this_month(self):
        from django.utils import timezone
        now = timezone.now()
        return self.expense_set.filter(
            date__year=now.year,
            date__month=now.month
        ).aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0')


class Expense(models.Model):
    title = models.CharField(max_length=200)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    date = models.DateField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.amount} PLN"


class Budget(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    monthly_limit = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    month = models.IntegerField()
    year = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['category', 'month', 'year', 'user']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.category.name} - {self.monthly_limit} PLN ({self.month}/{self.year})"

    def spent(self):
        return self.category.expense_set.filter(
            date__year=self.year,
            date__month=self.month,
            user=self.user
        ).aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0')

    def remaining(self):
        return self.monthly_limit - self.spent()

    def percent_used(self):
        if self.monthly_limit == 0:
            return 0
        return min(int((self.spent() / self.monthly_limit) * 100), 100)
