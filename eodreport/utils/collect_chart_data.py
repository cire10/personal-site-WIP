import quandl
import datetime
import requests
import pandas as pd
import os
from eodreport.utils import read_config
import datetime


iex_p_api_key = read_config.get_iex_p_api_key()
iex_s_api_key = read_config.get_iex_s_api_key()

quandl.ApiConfig.api_key = read_config.get_quandl_api_key()

dir_path = os.path.dirname(os.path.realpath(__file__))
base_data_folder_dir = dir_path + '/data/'


str_today = datetime.date.today().strftime('%Y%m%d')


def _get_file_path_log():
    return f'{base_data_folder_dir}/log.csv'


def _get_file_path_daily_equities():
    return f'{base_data_folder_dir}/{str_today}.csv'


def _get_file_path_sp500_holdings():
    return f'{base_data_folder_dir}/sp500_holdings.csv'


def _get_file_path_treasury_rates():
    return f'{base_data_folder_dir}/treasury_rates.csv'


def _get_file_path_corp_bond_sector_yields(grade):
    return f'{base_data_folder_dir}/{grade}_yields.csv'


def update_time_series_csv(file_path, df):
    df_updated = df
    if os.path.isfile(file_path):
        # all data date format should be 'YYYYMMDD'
        df_old = pd.read_csv(file_path, index_col='Date',
                             dtype={'Date': 'string'})
        df_updated = df_old.append(df)
        df_updated = df_updated[~df_updated.index.duplicated(keep='first')]
        df_updated.sort_index(inplace=True)
    df_updated.to_csv(file_path)


def divide_list_to_length(l, length):
    for i in range(0, len(l), length):
        yield l[i:i + length]


def _filter_equities_quote_dict(d):
    quote_keep_keys = ('open',
                       'high',
                       'low',
                       'close',
                       'previousClose',
                       'volume',
                       'previousVolume',
                       'avgTotalVolume',
                       'changePercent')
    return {key: d[key] for key in quote_keep_keys}


def _update_file_daily_equities():

    tickers = pd.read_csv(_get_file_path_sp500_holdings(),
                          usecols=['Ticker'])['Ticker']

    base_iex_api_url = 'https://sandbox.iexapis.com/stable/'
    d = {}
    for l_tickers in divide_list_to_length(tickers, 100):
        s_symbols = ','.join(l_tickers)
        url = base_iex_api_url + \
            f'stock/market/batch?symbols={s_symbols}&types=quote&token={iex_p_api_key}'

        json_response = requests.get(url).json()

        d_partial = {}
        for key, value in json_response.items():
            d_partial[key] = _filter_equities_quote_dict(value['quote'])

        d.update(d_partial)

    df = pd.DataFrame.from_dict(d, orient='index')
    df.index.name = 'Ticker'
    df.to_csv(_get_file_path_daily_equities())


def _update_file_sp500_holdings():
    url = 'https://www.ssga.com/us/en/individual/etfs/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx'
    df = pd.read_excel(url, usecols=['Ticker', 'Weight', 'Sector'], skiprows=4)
    df = df[~df['Ticker'].str.contains('CASH', na=True)]
    df['Weight'] = df['Weight'] / 100
    df.to_csv(_get_file_path_sp500_holdings(), index=False)


def _update_file_treasury_rates():
    def get_data(days):
        df = quandl.get('USTREASURY/YIELD', rows=days)
        df.index = df.index.strftime('%Y%m%d')
        for column in df.columns.values.tolist():
            df[column] = df[column] / 100
        return df

    file_path = _get_file_path_treasury_rates()
    if os.path.isfile(file_path) and len(pd.read_csv(file_path)) > 364:
        df_ust_rates = get_data(1)
        update_time_series_csv(file_path, df_ust_rates)
    else:
        df_ust_rates = get_data(365)
        df_ust_rates.to_csv(file_path)


def _clean_ishares_bond_etfs_data(df):

    d_ishares_sector_mapping = {
        'Communications': 'Communication Services',
        'Capital Goods': 'Industrials',
        'Insurance': 'Financials',
        'Consumer Cyclical': 'Consumer Discretionary',
        'Brokerage/Asset Managers/Exchanges': 'Financials',
        'Financial Other': 'Financials',
        'Finance Companies': 'Financials',
        'Banking': 'Financials',
        'Consumer Non-Cyclical': 'Consumer Staples',
        'Technology': 'Information Technology',
        'Basic Industry': 'Materials',
        'Energy': 'Energy',
        'Reits': 'Real Estate',
        'Transportation': 'Industrials',
        'Electric': 'Energy',
        'Industrial Other': 'Industrials'
    }

    # formatting the col names
    df.columns = [name if '(%)' not in name else name[:(
        name.find('(%)') - 1)] for name in df.columns]

    # filtering out unnecessary values
    df = df[df['Asset Class'] == 'Fixed Income']
    df = df[df['YTM'] != '-']
    df = df[df['Sector'] != 'Owned No Guarantee']

    # applying percentages
    l = ['Weight', 'YTM', 'Coupon', 'Real YTM']
    for col in l:
        df[col] = pd.to_numeric(df[col]) / 100

    # remapping the sectors to be consistent with SPY ETF
    df['Sector'] = df['Sector'].map(d_ishares_sector_mapping)

    # years to maturity
    # df_hyg['Maturity'] = (pd.to_datetime(df_hyg['Maturity']) - e_date) / datetime.timedelta(days = 365)
    return df


def _update_file_corp_bond_sector_yields(url, grade):
    df = pd.read_csv(url, skiprows=9)
    df = _clean_ishares_bond_etfs_data(df)
    df = df[['Real YTM', 'Sector']].groupby('Sector').mean()
    df.columns = [str_today]
    df = df.transpose()
    df.index.name = 'Date'
    file_path = _get_file_path_corp_bond_sector_yields(grade)
    update_time_series_csv(file_path, df)


def _update_file_lqd_sector_yields():
    url = 'https://www.ishares.com/us/products/239566/ishares-iboxx-investment-grade-corporate-bond-etf/1467271812596.ajax?fileType=csv&fileName=LQD_holdings&dataType=fund'
    _update_file_corp_bond_sector_yields(url, 'lqd')


def _update_file_hyg_sector_yields():
    url = 'https://www.ishares.com/us/products/239565/ishares-iboxx-high-yield-corporate-bond-etf/1467271812596.ajax?fileType=csv&fileName=HYG_holdings&dataType=fund'
    _update_file_corp_bond_sector_yields(url, 'hyg')


def update_all_data():
    _update_file_hyg_sector_yields()
    _update_file_lqd_sector_yields()
    _update_file_treasury_rates()
    _update_file_sp500_holdings()
    _update_file_daily_equities()


def check_data():
    df_log = pd.read_csv(_get_file_path_log(),
                         index_col=['Date'],
                         dtype={'Date': 'string'})
    if str_today not in df_log.index.values:
        update_all_data()
        df_update = pd.DataFrame.from_dict({'Date': [str_today],
                                            'Updated': ['True']})
        df_update.to_csv(_get_file_path_log(), mode='a',
                         header=False, index=False)


def get_lqd_yields():
    return pd.read_csv(_get_file_path_corp_bond_sector_yields('lqd'), index_col='Date')


def get_hyg_yields():
    return pd.read_csv(_get_file_path_corp_bond_sector_yields('hyg'), index_col='Date')


def get_equities_data():
    df_sp500 = pd.read_csv(_get_file_path_sp500_holdings())
    df_daily_equities = pd.read_csv(_get_file_path_daily_equities())
    df = pd.merge(df_sp500, df_daily_equities,
                  left_index=True, right_index=True)
    df.drop(columns=['Ticker_y'], inplace=True)
    df.rename({'Ticker_x': 'Ticker'}, inplace=True)
    return df


def get_treasury_rates():
    return pd.read_csv(_get_file_path_treasury_rates(), index_col='Date')


if __name__ == "__main__":
    update_all_data()
