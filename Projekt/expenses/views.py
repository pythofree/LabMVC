import json
import ssl
import urllib.request
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import RegisterForm, LoginForm, ExpenseForm, CategoryForm, BudgetForm
from .models import Expense, Category, Budget


# ── AUTH ──────────────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Account created successfully!')
        return redirect('dashboard')
    return render(request, 'expenses/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'expenses/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    now = timezone.now()
    expenses = Expense.objects.filter(user=request.user)

    # This month stats
    this_month = expenses.filter(date__year=now.year, date__month=now.month)
    total_month = this_month.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    total_all = expenses.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

    # By category for chart
    cat_data = (
        this_month.values('category__name', 'category__color')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    chart_labels = [d['category__name'] or 'No category' for d in cat_data]
    chart_amounts = [float(d['total']) for d in cat_data]
    chart_colors = [d['category__color'] or '#6c757d' for d in cat_data]

    # Monthly chart (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        month = now.month - i
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        total = expenses.filter(date__year=year, date__month=month).aggregate(
            Sum('amount'))['amount__sum'] or 0
        import calendar
        monthly_data.append({'label': f"{calendar.month_abbr[month]} {year}", 'total': float(total)})

    # Budgets status
    budgets = Budget.objects.filter(user=request.user, month=now.month, year=now.year)
    recent_expenses = expenses[:5]

    return render(request, 'expenses/dashboard.html', {
        'total_month': total_month,
        'total_all': total_all,
        'chart_labels': json.dumps(chart_labels),
        'chart_amounts': json.dumps(chart_amounts),
        'chart_colors': json.dumps(chart_colors),
        'monthly_labels': json.dumps([d['label'] for d in monthly_data]),
        'monthly_amounts': json.dumps([d['total'] for d in monthly_data]),
        'budgets': budgets,
        'recent_expenses': recent_expenses,
        'now': now,
    })


# ── EXPENSES ──────────────────────────────────────────────────────────────────

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)

    # Filters
    category_id = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-date')

    if category_id:
        expenses = expenses.filter(category_id=category_id)
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
    if search:
        expenses = expenses.filter(title__icontains=search)

    allowed_sorts = ['date', '-date', 'amount', '-amount', 'title', '-title']
    if sort in allowed_sorts:
        expenses = expenses.order_by(sort)

    total = expenses.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    categories = Category.objects.filter(user=request.user)

    return render(request, 'expenses/expense_list.html', {
        'expenses': expenses,
        'categories': categories,
        'total': total,
        'selected_category': category_id,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
        'sort': sort,
    })


@login_required
def expense_create(request):
    form = ExpenseForm(request.user, request.POST or None, initial={'date': date.today()})
    if request.method == 'POST' and form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        expense.save()
        messages.success(request, 'Expense added successfully!')
        return redirect('expense_list')
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Add Expense'})


@login_required
def expense_update(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    form = ExpenseForm(request.user, request.POST or None, instance=expense)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Expense updated successfully!')
        return redirect('expense_list')
    return render(request, 'expenses/expense_form.html', {'form': form, 'title': 'Edit Expense'})


@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted.')
        return redirect('expense_list')
    return render(request, 'expenses/confirm_delete.html', {'object': expense, 'type': 'expense'})


# ── CATEGORIES ────────────────────────────────────────────────────────────────

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'expenses/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cat = form.save(commit=False)
        cat.user = request.user
        cat.save()
        messages.success(request, 'Category created!')
        return redirect('category_list')
    return render(request, 'expenses/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_update(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    form = CategoryForm(request.POST or None, instance=cat)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category updated!')
        return redirect('category_list')
    return render(request, 'expenses/category_form.html', {'form': form, 'title': 'Edit Category'})


@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, 'Category deleted.')
        return redirect('category_list')
    return render(request, 'expenses/confirm_delete.html', {'object': cat, 'type': 'category'})


# ── BUDGETS ───────────────────────────────────────────────────────────────────

@login_required
def budget_list(request):
    now = timezone.now()
    budgets = Budget.objects.filter(user=request.user, month=now.month, year=now.year)
    return render(request, 'expenses/budget_list.html', {'budgets': budgets, 'now': now})


@login_required
def budget_create(request):
    now = timezone.now()
    form = BudgetForm(request.user, request.POST or None,
                      initial={'month': now.month, 'year': now.year})
    if request.method == 'POST' and form.is_valid():
        budget = form.save(commit=False)
        budget.user = request.user
        budget.save()
        messages.success(request, 'Budget set!')
        return redirect('budget_list')
    return render(request, 'expenses/budget_form.html', {'form': form, 'title': 'Set Budget'})


@login_required
def budget_update(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    form = BudgetForm(request.user, request.POST or None, instance=budget)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Budget updated!')
        return redirect('budget_list')
    return render(request, 'expenses/budget_form.html', {'form': form, 'title': 'Edit Budget'})


@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted.')
        return redirect('budget_list')
    return render(request, 'expenses/confirm_delete.html', {'object': budget, 'type': 'budget'})


# ── CURRENCY SWITCH ───────────────────────────────────────────────────────────

def fetch_rates():
    url = 'https://api.nbp.pl/api/exchangerates/tables/A/?format=json'
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(url, timeout=5, context=ctx) as response:
        data = json.loads(response.read())
        return data[0]['rates']


@login_required
def set_currency(request):
    code = request.GET.get('code', 'PLN')
    if code == 'PLN':
        request.session['currency_code'] = 'PLN'
        request.session['currency_rate'] = '1'
    else:
        try:
            rates = fetch_rates()
            for r in rates:
                if r['code'] == code:
                    request.session['currency_code'] = code
                    request.session['currency_rate'] = str(r['mid'])
                    break
        except Exception:
            pass
    return redirect(request.GET.get('next', 'dashboard'))


# ── CURRENCY API ──────────────────────────────────────────────────────────────

@login_required
def currency_rates(request):
    rates = []
    error = None
    converted = None
    amount_pln = request.GET.get('amount', '')
    selected_currency = request.GET.get('currency', '')

    try:
        rates = fetch_rates()

        if amount_pln and selected_currency:
            amount = Decimal(str(amount_pln))
            for r in rates:
                if r['code'] == selected_currency:
                    converted = round(amount / Decimal(str(r['mid'])), 2)
                    break
    except Exception as e:
        error = 'Could not fetch exchange rates. Please try again later.'

    return render(request, 'expenses/currency.html', {
        'rates': rates,
        'error': error,
        'converted': converted,
        'amount_pln': amount_pln,
        'selected_currency': selected_currency,
    })
