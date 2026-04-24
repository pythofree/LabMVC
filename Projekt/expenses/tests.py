import datetime
from decimal import Decimal

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Category, Expense, Budget


class CategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='testpass123')
        self.category = Category.objects.create(name='Food', color='#ff0000', user=self.user)

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Food')

    def test_total_spent_this_month_no_expenses(self):
        self.assertEqual(self.category.total_spent_this_month(), Decimal('0'))

    def test_total_spent_this_month_with_expenses(self):
        today = datetime.date.today()
        Expense.objects.create(title='Lunch', amount=Decimal('25.00'), date=today,
                               category=self.category, user=self.user)
        self.assertEqual(self.category.total_spent_this_month(), Decimal('25.00'))


class ExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser2', password='testpass123')
        self.category = Category.objects.create(name='Transport', color='#00ff00', user=self.user)

    def test_expense_str(self):
        expense = Expense.objects.create(
            title='Bus ticket', amount=Decimal('3.50'),
            date=datetime.date.today(), user=self.user
        )
        self.assertEqual(str(expense), 'Bus ticket - 3.50 PLN')

    def test_expense_without_category(self):
        expense = Expense.objects.create(
            title='Misc', amount=Decimal('10.00'),
            date=datetime.date.today(), user=self.user
        )
        self.assertIsNone(expense.category)


class BudgetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser3', password='testpass123')
        self.category = Category.objects.create(name='Entertainment', color='#0000ff', user=self.user)
        today = datetime.date.today()
        self.budget = Budget.objects.create(
            category=self.category, monthly_limit=Decimal('500.00'),
            month=today.month, year=today.year, user=self.user
        )

    def test_budget_str(self):
        self.assertIn('Entertainment', str(self.budget))

    def test_budget_spent_empty(self):
        self.assertEqual(self.budget.spent(), Decimal('0'))

    def test_budget_remaining(self):
        self.assertEqual(self.budget.remaining(), Decimal('500.00'))

    def test_budget_percent_used_zero(self):
        self.assertEqual(self.budget.percent_used(), 0)

    def test_budget_percent_used_with_expense(self):
        today = datetime.date.today()
        Expense.objects.create(title='Cinema', amount=Decimal('250.00'),
                               date=today, category=self.category, user=self.user)
        self.assertEqual(self.budget.percent_used(), 50)


class ViewAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('viewuser', password='testpass123')

    def test_dashboard_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_accessible_when_logged_in(self):
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_expense_list_requires_login(self):
        response = self.client.get(reverse('expense_list'))
        self.assertEqual(response.status_code, 302)

    def test_login_page_accessible(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_accessible(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_add_expense(self):
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.post(reverse('expense_create'), {
            'title': 'Test expense',
            'amount': '50.00',
            'date': datetime.date.today().isoformat(),
            'description': '',
        })
        self.assertEqual(Expense.objects.filter(user=self.user).count(), 1)

    def test_expense_belongs_to_user(self):
        other_user = User.objects.create_user('other', password='testpass123')
        category = Category.objects.create(name='X', color='#000', user=other_user)
        expense = Expense.objects.create(title='Other', amount=Decimal('10.00'),
                                         date=datetime.date.today(), user=other_user)
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.get(reverse('expense_update', args=[expense.pk]))
        self.assertEqual(response.status_code, 404)
