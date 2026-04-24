def currency(request):
    code = request.session.get('currency_code', 'PLN')
    rate = request.session.get('currency_rate', '1')
    return {
        'currency_code': code,
        'currency_rate': rate,
    }
