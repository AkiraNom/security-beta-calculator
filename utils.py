
import pandas as pd
import yfinance as yf
import datetime
import plotly.graph_objects as go
import plotly.express as px
import statsmodels.api as sm
import streamlit as st


class StockData:

    @staticmethod
    def validate_ticker_symbol(ticker):
        if not yf.download(ticker).empty:
            return ticker
        else:
            st.warning(f"No Data found for : {ticker}. It might be delisted. Please try another ticker")
            st.stop()

    @staticmethod
    def fetch_stock_data(ticker_symbols:str, start:str, end:str, interval:str):
        #get stock price data from yahoo finance
        data = yf.download(tickers=ticker_symbols, start=start, end=end, interval=interval)
        current_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
        return data, current_time

    @staticmethod
    def calculate_returns(data, ticker):
        # calculate weekly or monthly return
        return data['Close'][ticker].pct_change(1)

    @classmethod
    def stock_return(cls, data, ticker_symbols, index_name):
        ticker_symbol, index_symbol = *ticker_symbols,
        ticker_return = cls.calculate_returns(data, ticker_symbol)
        index_return = cls.calculate_returns(data, index_symbol)
        df = pd.DataFrame({f'{ticker_symbol}_return': ticker_return,
                           f'{index_name}_return': index_return})

        return df

    @staticmethod
    def estimate_beta(df):

        cov = df.cov().iloc[0,1]
        # market return at the column 1
        var = df.iloc[:,1].var()

        beta_cov = cov/var
        # OLS Regression method
        X = df.iloc[1:,1].values.reshape(-1,1)  # Index returns
        y = df.iloc[1:,0].values  # Stock returns
        X = sm.add_constant(X)  # Add a constant term to the predictor
        model = sm.OLS(y, X).fit()
        beta_ols = model.params[1]

        return beta_cov,beta_ols, model.summary()


class Plots:

    @staticmethod
    def candle_chart(df, ticker, current_time, index_ticker=False, index_ticker_map=None):

        if index_ticker:
            name = [k for k, v in index_ticker_map.items() if v == ticker][0]
        else:
            name = ticker

        fig= go.Figure(go.Candlestick(x=df.index,
                                      open=df['Open'][ticker],
                                      high=df['High'][ticker],
                                      low=df['Low'][ticker],
                                      close=df['Close'][ticker],
                                      name=f'Candle_{name}',
                                      ))

        fig.update_layout(
            title = f'<b>{name} Candle Chart </b>',
            height=700,
            xaxis = dict(tickfont = dict(size=16)),
            yaxis = dict(title=dict(text='stock price ($)'), tickfont = dict(size=16)))

        # footer
        data_source = f'<b>Source: <a href="https://www.yahoofinance.com/">Yahoo! Finance </a> Time : {current_time}</b>'

        fig.add_annotation(
                showarrow=False,
                text=data_source,
                font=dict(color='black',size=15),
                xref='x domain',
                x=0.0,
                yref='y domain',
                y=-0.4
                )

        return fig

    @staticmethod
    def scatter_plot(df, x, y, trendline=None):
        fig = px.scatter(df, x, y, trendline=trendline)

        return fig

