import sys
import os
import math
import json
from collections import Counter

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Add backtest-engine directory to Python path so we can import its modules
_BACKTEST_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'backtest-engine')
)
if _BACKTEST_DIR not in sys.path:
    sys.path.insert(0, _BACKTEST_DIR)


def _json_body(request):
    return json.loads(request.body)


@csrf_exempt
@require_http_methods(["POST"])
def factorial(request):
    try:
        data = _json_body(request)
        n = int(data['n'])
        if n < 0:
            return JsonResponse({'error': 'n must be non-negative'}, status=400)
        return JsonResponse({'result': math.factorial(n)})
    except (KeyError, ValueError, TypeError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def combination(request):
    try:
        data = _json_body(request)
        n, k = int(data['n']), int(data['k'])
        if n < 0 or k < 0 or k > n:
            return JsonResponse(
                {'error': 'Invalid input: need 0 \u2264 k \u2264 n'}, status=400
            )
        result = math.factorial(n) // (math.factorial(k) * math.factorial(n - k))
        return JsonResponse({'result': result})
    except (KeyError, ValueError, TypeError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def permutations(request):
    try:
        data = _json_body(request)
        word = data['word'].strip().lower()
        if not word:
            return JsonResponse({'error': 'Word cannot be empty'}, status=400)
        if not word.isalpha():
            return JsonResponse({'error': 'Word must contain letters only'}, status=400)
        total = math.factorial(len(word))
        for count in Counter(word).values():
            total //= math.factorial(count)
        return JsonResponse({'result': total})
    except (KeyError, ValueError, TypeError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def combination_product(request):
    try:
        data = _json_body(request)
        pairs = data.get('pairs', [])
        if not pairs:
            return JsonResponse({'error': 'At least one C(n, k) pair required'}, status=400)
        product = 1
        for pair in pairs:
            n, k = int(pair['n']), int(pair['k'])
            if n < 0 or k < 0 or k > n:
                return JsonResponse(
                    {'error': f'Invalid pair: n={n}, k={k} — need 0 \u2264 k \u2264 n'},
                    status=400,
                )
            product *= math.factorial(n) // (math.factorial(k) * math.factorial(n - k))
        return JsonResponse({'result': product})
    except (KeyError, ValueError, TypeError) as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def run_backtest(request):
    try:
        data = _json_body(request)
        ticker = data.get('ticker', 'SPY').strip().upper()
        start_date = data.get('start_date', '2020-01-01')
        end_date = data.get('end_date', '2024-01-01')
        window = int(data.get('window', 20))
        z_threshold = float(data.get('z_threshold', 2.0))

        if not ticker:
            return JsonResponse({'error': 'Ticker is required'}, status=400)
        if window < 2:
            return JsonResponse({'error': 'Window must be at least 2'}, status=400)
        if z_threshold <= 0:
            return JsonResponse({'error': 'Z-threshold must be positive'}, status=400)

        from data_handler import fetch_data
        from strategy import generate_signals
        from analytics import calculate_returns

        df = fetch_data(ticker, start_date, end_date)
        df = generate_signals(df, window=window, z_threshold=z_threshold)
        df = calculate_returns(df)

        # Shift signal by 1 to prevent lookahead bias (same as backtest-engine/main.py)
        df['Strategy_Return'] = df['Signal'].shift(1) * df['Daily_Return']
        df.dropna(inplace=True)

        if df.empty:
            return JsonResponse({'error': 'No data returned for the given ticker and date range'}, status=400)

        market_cum_return = float((df['Daily_Return'] + 1).prod() - 1)
        strategy_cum_return = float((df['Strategy_Return'] + 1).prod() - 1)

        market_sharpe = float(
            (df['Daily_Return'].mean() * 252) / (df['Daily_Return'].std() * (252 ** 0.5))
        )
        strategy_sharpe = float(
            (df['Strategy_Return'].mean() * 252) / (df['Strategy_Return'].std() * (252 ** 0.5))
        )

        market_cum_series = (1 + df['Daily_Return']).cumprod()
        strategy_cum_series = (1 + df['Strategy_Return']).cumprod()

        return JsonResponse({
            'ticker': ticker,
            'start_date': start_date,
            'end_date': end_date,
            'market_cumulative_return': round(market_cum_return, 6),
            'strategy_cumulative_return': round(strategy_cum_return, 6),
            'market_sharpe': round(market_sharpe, 4),
            'strategy_sharpe': round(strategy_sharpe, 4),
            'chart': {
                'dates': df.index.strftime('%Y-%m-%d').tolist(),
                'market': [round(float(v), 6) for v in market_cum_series],
                'strategy': [round(float(v), 6) for v in strategy_cum_series],
            },
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
