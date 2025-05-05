import os
import pickle
import warnings
import dateutil.parser as parser
import io

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import networkx as nx

def get_start_dates_tlg(root='Telegram_data'):
    files = os.listdir(f'{root}')
    files.remove('.ipynb_checkpoints')
    fig, axs = plt.subplots(nrows=len(files)//3 + 1, ncols=3, figsize=(25, 50))
    plt.subplots_adjust(hspace=0.5)
    fig.suptitle("Количество новостей по каналам по дням", fontsize=30)
    fig.tight_layout()

    for file, ax in zip(files, axs.ravel()):
        tmp = pd.read_json(f'{root}/{file}')['date'].dt.round('D')
        date = tmp.iloc[-1]
        ax.hist(tmp, bins=len(np.unique(tmp)))
        ax.set_title(f'{file[:-14]} начал работу {date}')
    plt.show()
    
def get_dates_tlg(root='Telegram_data'):
    files = os.listdir(f'{root}')
    files.remove('.ipynb_checkpoints')
    dates = pd.Series()
    for file in files:
        tmp = pd.to_datetime(pd.read_json(f'{root}/{file}')['date']).dt.round('D')
        dates = pd.concat([dates, tmp], axis=0)
    
    return dates

def avg_time_tg(root='Telegram_prep'):
    roots = os.listdir(f'{root}')
    roots.remove('.ipynb_checkpoints')
    df = pd.DataFrame()
    for root in roots:
        date = pd.read_csv(f'Telegram_prep/{root}', low_memory=False)['date']
        date = pd.to_datetime(date).sort_values() 
        delta = (date - date.shift(1)).dt.total_seconds().fillna(0)  # заменяем NaN нулями
        avg_time = delta.mean() / 60
        max_time = delta.max() / 60
        min_time = delta.min() / 60
        times = pd.DataFrame([[root[:-4], min_time, avg_time, max_time]], columns=['Источник', 'Минимальное время', 'Среднее время', 'Максимальное время'])
        df = pd.concat([df, times], axis=0).reset_index(drop=True)
    return df

def plot_company_news_hist_tg(companies):
    cols = ['date'] + [i for i in companies.keys()]
    agg_df = pd.DataFrame()
    roots = os.listdir('Telegram_prep')
    if '.ipynb_checkpoints' in roots:
        roots.remove('.ipynb_checkpoints')
    if 'messages' in roots:
        roots.remove('messages')
    for root in roots:
        df = pd.read_csv(f'Telegram_prep/{root}', low_memory=False)
        df = df[cols]
        agg_df = pd.concat([agg_df, df])
    
    agg_df['date'] = pd.to_datetime(agg_df['date'])
    
    fig, axs = plt.subplots(nrows=len(companies)//3 + 1, ncols=3, figsize=(25, 50))
    plt.subplots_adjust(hspace=0.5)
    fig.suptitle("Количество новостей по компаниям", fontsize=30, y=1.02)
    fig.tight_layout()

    for company, ax in zip(companies, axs.ravel()):
        date = agg_df[agg_df[company] == True]['date'].dt.round('D')
        
        try:
            ax.hist(date, bins=len(np.unique(date)))
        except ValueError as ex:
            print(ex)
            print(f'{company}')
            
        ax.set_title(f'{company}; {len(date)} news')

    plt.show()

#????????????????????????????????????????????   
def plot_sector_news_hist_tg(sectors):
    cols = ['date'] + [i for i in sectors]
    agg_df = pd.DataFrame()
    roots = os.listdir('Telegram_prep')
    if '.DS_Store' in roots:
        roots.remove('.DS_Store')
    if 'messages' in roots:
        roots.remove('messages')
    for root in roots:
        df = pd.read_csv(f'Telegram_prep/{root}', low_memory=False)
        df = df[cols]
        agg_df = pd.concat([agg_df, df])
    
    agg_df['date'] = pd.to_datetime(agg_df['date'])
    
    fig, axs = plt.subplots(nrows=len(sectors)//3 + 1, ncols=3, figsize=(25, 50))
    plt.subplots_adjust(hspace=0.5)
    fig.suptitle("Количество новостей по секторам", fontsize=30, y=1.02)
    fig.tight_layout()

    for sector, ax in zip(sectors, axs.ravel()):
        date = agg_df[agg_df[sector] == True]['date'].dt.round('D')
        
        try:
            ax.hist(date, bins=len(np.unique(date)))
        except ValueError as ex:
            print(ex)
            print(f'{sector}')
            
        ax.set_title(f'{sector}; {len(date)} news')

    plt.show()