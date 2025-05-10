import re
import os
import warnings

import sys
import numpy as np
import pandas as pd
from pymystem3 import Mystem
from nltk.corpus import stopwords
mystem = Mystem()


def preprocess_tg(file, swords):
    try:
        df = pd.read_json(f'Telegram_data/{file}')[['date', 'message', 'views', 'forwards', 'fwd_from']].dropna(subset='message')
        n_rows = df.shape[0]
        c = 0
        cols = ['message']
        for col in cols:
            df[col] = df[col].str.replace('\n', '')
            df[col] = df[col].str.replace(r'W+', ' ', regex=True)
            df[col] = df[col].str.lower()
            while c < n_rows:
                res = []
                doc = []
                large_str = ' '.join([txt + ' splitter ' for txt in df[col][c:c+1000]])
                large_str = mystem.lemmatize(large_str)

                for word in large_str:
                    if word.strip() != '' and word not in swords:
                        if word == 'splitter':
                            if len(doc) == 0:
                                doc.append('')
                            res.append(doc)
                            doc = []
                        else:
                            doc.append(word)
                del large_str
                del doc
                res = [' '.join(lst) for lst in res]
                df[col][c:c+1000] = res
                c += 1000
            print(f'{col} ready')
        return df
    except KeyboardInterrupt:
        raise
    except Exception as ex:
        print(ex)
        return None


def add_company_tg(for_regex, companies):
    files = os.listdir('Telegram_prep')
    #files.remove('messages')
    if '.ipynb_checkpoints' in files:
        files.remove('.ipynb_checkpoints')
    for file in files:
        df = pd.read_csv(f'Telegram_prep/{file}')
        for company in companies:
            reg = for_regex[company]
            reg = ' | '.join(reg)
            in_str = df['message'].str.contains(reg)
            df[company] = in_str
        df.to_csv(f'Telegram_prep/{file}', index=False)
        print(f'{file} done')

def add_industry_tg(companies, for_regex_industry):
    files = os.listdir('Telegram_prep')
    files.remove('messages')
    if '.ipynb_checkpoints' in files:
        files.remove('.ipynb_checkpoints')
    for file in files:
        df = pd.read_csv(f'Telegram_prep/{file}')
        for industry in industries:
            reg = for_regex_industry[industry]
            reg = ' | '.join(reg)
            in_str = df['message'].str.contains(reg)
            df[industry] = in_str
        df.to_csv(f'Telegram_prep/{file}', index=False)
        print(f'{file} done')
        
        
def add_target_tg(companies):
    cols = ['1 мин.']
    times = [pd.Timedelta(1, unit='min')]
    deltas = {i:j for i, j in zip(cols, times)}
    comp = [com for com in companies]
    files = os.listdir(f'Telegram_prep')
    if '.ipynb_checkpoints' in files:
        files.remove('.ipynb_checkpoints')
    for file in files:
        df = pd.read_csv(f'Telegram_prep/{file}')
        if 'timestamp' in df.columns:
            df.rename(columns={'timestamp':'date'})
        df = df[df['date'] != 'No time']
        df['date'] = pd.to_datetime(df['date'])
        if df['date'].iloc[0].tz is None:
            df['date'] = df['date'].astype("datetime64[ns]")
        else:
            df['date'] = df['date'].dt.tz_localize(None).astype("datetime64[ns]")

        df.drop_duplicates(inplace=True)
        df.sort_values('date', ignore_index=True, inplace=True)

        for com in comp:
            price = pd.read_csv(f'Stock_data/1 мин./{com}.csv')
            price['timestamp'] = pd.to_datetime(price['timestamp']).astype("datetime64[ns]")
            price.rename(columns={'timestamp':'date'}, inplace=True)
            price.sort_values('date', ignore_index=True, inplace=True)
            for col in cols:
                df['date'] += deltas[col]
                df = pd.merge_asof(df, price, on='date', direction='forward')
                df.rename(columns={'close': f'{col} {com} close'}, inplace=True)
                df['date'] -= deltas[col]
            print(f'{com} готов')
        df.to_csv(f'Telegram_prep/{file[:-13]}.csv', index=False)

def add_target_bin_tg(companies):
    cols = ['1 мин.']
    times = [pd.Timedelta(1, unit='min')]
    deltas = {i:j for i, j in zip(cols, times)}
    comp = [com for com in companies]
    files = os.listdir(f'Telegram_prep')
    
    if '.ipynb_checkpoints' in files:
        files.remove('.ipynb_checkpoints')
    if 'messages' in files:
        files.remove('messages')
    
    for file in files:
        df = pd.read_csv(f'Telegram_prep/{file}')
        df['date'] = pd.to_datetime(df['date'])
        if df['date'].iloc[0].tz is None:
            df['date'] = df['date'].astype("datetime64[ns]")
        else:
            df['date'] = df['date'].dt.tz_localize(None).astype("datetime64[ns]")

        df.sort_values(by='date', inplace=True)

        for com in comp:
            price = pd.read_csv(f'Stock_data/1 мин./{com}.csv')
            price['timestamp'] = pd.to_datetime(price['timestamp']).astype("datetime64[ns]")
            price.rename(columns={'timestamp':'date'}, inplace=True)
            price.sort_values('date', ignore_index=True, inplace=True)
            prev_price = pd.merge_asof(df, price, on='date', direction='backward')['close']
            for col in cols:
                df['date'] += deltas[col]
                df = pd.merge_asof(df, price, on='date', direction='forward')
                df['close'] = prev_price < df['close']
                df.rename(columns={'close': f'{col} {com} close_bin'}, inplace=True)
                df['date'] -= deltas[col]
            print(f'{com} готов')
        df.to_csv(f'Telegram_prep/{file[:-13]}.csv', index=False)

def telegram_to_standard_date():
    files = os.listdir('Telegram_prep')
    if '.ipynb_checkpoints' in files:
        files.remove('.ipynb_checkpoints')

    for file in files:
        print(f'Обрабатывается файл {file}')
        df = pd.read_csv(f'Telegram_prep/{file}')
        df['date'] = pd.to_datetime(df['date'].map(lambda x: x[:-6]))
        df.to_csv(f'Telegram_prep/{file}', index=False)