# analysis packages
from eodreport.utils import collect_chart_data
import pandas as pd
import datetime

import plotly.graph_objs as go
import plotly.offline as opy
from plotly.subplots import make_subplots

import os
dir_path = os.path.dirname(os.path.realpath(__file__))
base_chart_folder_dir = dir_path + '/charts/'


class equities_charts():

    @staticmethod
    def chart_sector_flow(equities):
        # month flow
        # daily flow
        equities['flow'] = (equities['close'] -
                            equities['previousClose']) * equities['volume']
        df_sector_flow = equities[['flow', 'Sector']].groupby('Sector').sum()

        fig = go.Figure(go.Bar(x=df_sector_flow.index,
                               y=df_sector_flow['flow']))
        return fig.to_html(full_html=False)

    @staticmethod
    def chart_top10_movers(equities):
        sectors = equities['Sector'].unique()

        d = {}
        for sector in sectors:
            df_sector = equities[equities['Sector'] == sector].sort_values(
                ['changePercent'], ascending=False).head(10)
            df_sector['text'] = round(
                df_sector['volume'] / df_sector['avgTotalVolume'], 2)
            df_sector['text'] = df_sector['text'].astype(str)
            df_sector['text'] = 'Ticker: ' + df_sector['Ticker_x'] + \
                ', Volume/30D AVG Volume: ' + df_sector['text'] + 'X'
            d[sector] = df_sector

        fig = go.Figure()
        for sector, df_sector_top10 in d.items():
            maxval, minval = df_sector_top10['Weight'].max(
            ), df_sector_top10['Weight'].min()
            sizes = [(((weight - minval)/(maxval - minval) + 1) * 100)
                     for weight in df_sector_top10['Weight']]
            fig.add_trace(go.Scatter(
                x=df_sector_top10['Sector'],
                y=df_sector_top10['changePercent'],
                text=df_sector_top10['text'],
                name=sector,
                mode='markers',
                marker=dict(size=sizes, sizemode='area')))
        fig.update_layout(yaxis=dict(tickformat=".2%"))
        return fig.to_html(full_html=False)


class corp_bond_etfs_charts():

    @staticmethod
    def chart_ig_hy_spread(lqd_yields, hyg_yields):
        lqd = lqd_yields.iloc[-1]
        hyg = hyg_yields.iloc[-1]
        fig = {
            'data': [go.Bar(x=hyg.index, y=hyg.values, name='HYG YTM'),
                     go.Bar(x=lqd.index, y=lqd.values, name='LQD YTM')],
            'layout': go.Layout(barmode='overlay', yaxis=dict(tickformat=".2%"))
        }
        fig = go.Figure(fig)
        # fig.write_html(f'{base_chart_folder_dir}ig_hy_spread.html')
        return fig.to_html(full_html=False)


class treasury_charts():

    @staticmethod
    def chart_todays_rates(rates):
        t_1_rates = rates.iloc[-1]
        t_2_rates = rates.iloc[-2]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t_1_rates.index, y=t_1_rates.values, mode='markers', name='T-1 Rates'))
        fig.add_trace(go.Scatter(
            x=t_2_rates.index, y=t_2_rates.values, mode='markers', name='T-2 Rates'))
        fig.update_layout(yaxis=dict(tickformat=".2%"))
        return fig.to_html(full_html=False)

    @staticmethod
    def chart_spreads(rates, front_tenor, back_tenor):
        spread = rates[back_tenor] - rates[front_tenor]
        spread.index = pd.to_datetime(spread.index, format='%Y%m%d')

        # historical levels
        chart_name = f'{front_tenor} vs {back_tenor}'
        fig = go.Figure(data=go.Scatter(x=spread.index, y=spread.values))
        fig.update_layout(title=chart_name, yaxis=dict(tickformat=".2%"))
        return fig.to_html(full_html=False)


def get_charts_context():

    # check if data have been updated
    collect_chart_data.check_data()

    charts_context = {}

    # treasury charts
    df_treasury_rates = collect_chart_data.get_treasury_rates()
    charts_context['ratesToday'] = treasury_charts.chart_todays_rates(
        df_treasury_rates)
    charts_context['ratesSpreads'] = treasury_charts.chart_spreads(
        df_treasury_rates, '2 YR', '10 YR')

    # corp bond etf charts
    df_lqd_yields = collect_chart_data.get_lqd_yields()
    df_hyg_yields = collect_chart_data.get_hyg_yields()
    charts_context['yieldsIGHY'] = corp_bond_etfs_charts.chart_ig_hy_spread(
        df_lqd_yields, df_hyg_yields)

    # equities charts
    df_equities = collect_chart_data.get_equities_data()
    charts_context['equitiesSectorFlow'] = equities_charts.chart_sector_flow(
        df_equities)
    charts_context['equitiesSectorTop10Movers'] = equities_charts.chart_top10_movers(
        df_equities)

    return charts_context
