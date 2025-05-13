from matplotlib import pyplot as plt
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import numpy as np

from parse_utils import get_news_for
from llm_utils import get_llm_coeff
from config import LLM_ALPHA

import requests
import logging
from io import BytesIO
from datetime import datetime, timedelta


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def get_stock_data(ticker: str):
    """Получение данных за 7 дней"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)
    
    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}/candles.json"
    
    all_data = []
    start = 0
    limit = 500

    while True:
        params = {
            'interval': 1,
            'from': start_date.strftime('%Y-%m-%d'),
            'till': end_date.strftime('%Y-%m-%d'),
            'start': start
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        candles = data['candles']['data']
        
        if not candles:
            break
        
        all_data.extend(candles)
        start += limit

    df = pd.DataFrame(all_data, columns=data['candles']['columns'])
    
    if not df.empty:
        df['begin'] = pd.to_datetime(df['begin'])
        df.set_index('begin', inplace=True)
        df = df.sort_index()
    
    return df



def plot_stock_data(df, ticker):
    """Построение графика акций."""

    today = pd.Timestamp.now().normalize()
    df_today = df[df.index.normalize() == today]

    plt.figure(figsize=(10, 5))
    plt.plot(df_today.index, df_today['close'], label='Цена закрытия')
    plt.title(f'График акций {ticker}')
    plt.xlabel('Время')
    plt.ylabel('Цена')
    plt.legend()
    plt.grid(True)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf


def forecast_exp(df):
    """Прогноз цены с использованием ARIMA (автоподбор параметров)"""

    model = ExponentialSmoothing(df['close'], trend='add').fit()
    forecast = model.forecast(60*4)

    return forecast

def forecast_fft(df, n_components=40):
    """Прогноз с использованием преобразования Фурье."""
    series = df['close']
    
    fft = np.fft.fft(series.values)

    indices = np.argsort(np.abs(fft))[::-1]
    main_indices = indices[:n_components * 2]

    filtered_fft = np.zeros_like(fft)
    filtered_fft[main_indices] = fft[main_indices]

    filtered_series = np.fft.ifft(filtered_fft).real

    last_period = filtered_series[-60 * 4:]
    forecast = np.tile(last_period, 1)

    return forecast

async def forecast_stock(df, ticker, message):
    messages = await get_news_for(ticker)

    await message.reply_text("Идёт предсказание цены.")

    forecast = (forecast_exp(df) + forecast_fft(df)) / 2
    forecast -= (forecast.iloc[0] - df['close'].iloc[-1])

    coef = get_llm_coeff(ticker, messages)
    forecast += np.array([coef * i * LLM_ALPHA for i in range(len(forecast))])

    return None, forecast


def plot_forecast(df, future_X, future_y, ticker):
    """График с прогнозом."""

    today = pd.Timestamp.now().normalize()
    df_today = df[df.index.normalize() == today]

    plt.figure(figsize=(10, 5))
    plt.plot(df_today.index, df_today['close'], label='Исторические данные')
    future_dates = pd.date_range(start=df_today.index[-1], periods=60  * 4, freq='T')
    plt.plot(future_dates, future_y, label='Прогноз', linestyle='--')
    plt.title(f'Прогноз акций {ticker}')
    plt.xlabel('Время')
    plt.ylabel('Цена')
    plt.legend()
    plt.grid(True)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf
