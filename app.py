import streamlit as st
import utils

st.set_page_config(
    page_title='Beta estimation',
    # layout='wide',
    # initial_sidebar_state='auto',
)

st.title(r'Beta ($\beta$) estimation')
st.markdown("""The beta (β) of an investment security is a measurement of its volatility of returns relative to the entire market.
               It is used as a measure of risk and is an integral part of the Capital Asset Pricing Model (CAPM).
               A company with a higher beta has greater risk and also greater expected returns.""")

st.header('Stock data', anchor='top-header', divider='gray')

st.subheader('Input parameters')

# input parameters
cols = st.columns(3)
with cols[0]:
    ticker1 = st.text_input(label='Type Ticker Symbol',value='AAPL')
    ticker_symbol = utils.StockData.validate_ticker_symbol(ticker1)
with cols[1]:
    options = ['SP500', 'Nasdaq', 'Dow Jones']
    index_ticker_map = {'SP500': '^SPX','Nasdaq':'^IXIC','Dow Jones': '^DJI'}
    selected_index = st.selectbox(label='Select market index', options=options)
    index_symbol = index_ticker_map[selected_index]
with cols[2]:
    options = ['1 week', '1 month']
    interval_map = {'1 week': '1wk','1 month':'1mo'}
    selected_interval = st.selectbox(label='Select interval', options=options)
    interval = interval_map[selected_interval]

ticker_symbols = [ticker_symbol, index_symbol]
st.write('')

cols = st.columns(2)
with cols[0]:
    start = st.date_input("Select start date", value=None)
with cols[1]:
    end = st.date_input("Select end date", value=None)

data, current_time = utils.StockData.fetch_stock_data(ticker_symbols, start, end, interval)

st.subheader('Stock Price')

tab1, tab2 = st.tabs([ticker_symbol, selected_index])
with tab1:
    st.plotly_chart(utils.Plots.candle_chart(data, ticker_symbol, current_time), use_container_width=True)

with tab2:
    st.plotly_chart(utils.Plots.candle_chart(data, index_symbol, current_time, index_ticker=True, index_ticker_map=index_ticker_map), use_container_width=True)

st.write()

st.header(r'$\beta$ estimation', divider='grey')

plot_type_map = {'1wk': 'Weekly', '1mo': 'Monthly'}
plot_type  = plot_type_map[interval]
st.subheader(f'{plot_type} Return')

df = utils.StockData.stock_return(data, ticker_symbols, selected_index)

with st.expander('View data table:'):
    st.dataframe(df)

st.subheader('Covariance/variance method')
st.markdown(r"""${\beta}$ in covariance/variance method is estimated using the following equation: <br>""", unsafe_allow_html=True)
st.latex(r"""\beta = Cov(r_i, r_m)/Var(r_m)""")
st.markdown("""
                - $r_i$ : expected return on an asset $i$
                - $r_m$ : average return on the market
            """, unsafe_allow_html=True)

st.subheader('Ordinary Least Squares (OLS) Regression Method')

# df.columns = ['AAPL_return', 'Nasdaq_return']
st.plotly_chart(utils.Plots.scatter_plot(df.iloc[1:,:], x=df.columns[1], y = df.columns[0], trendline='ols'))

st.subheader(r'Estimated $\beta$')

beta_cov, beta_ols, model_summary = utils.StockData.estimate_beta(df)

with st.container():
    st.code(f"""
            Covariance/variance method : {beta_cov:.5f}
            Ols method                 : {beta_ols:.5f} """)

cols = st.columns(2)
with cols[0]:
    adjustment_coefficient = st.slider('Beta adjustment coefficient', 0.0, 1.0, 2/3)
with cols[1]:
    with st.expander('Blume adjuetment'):
        st.info("""Blume adjustment (M. Blume 1971) is the most frequently used adjustment. The temporal instability
                and return tendency of the beta factors towards 1.0 is approximated in the Blume adjustment by the following equation:""")
        st.latex(r'\beta = coef. * \beta_0 + 1 * (1-coef.)')
        st.write('reference: [beta adjustment](https://www.smart-zebra.de/post/raw-beta-vs-adjusted-beta-choosing-the-right-beta-factors-in-the-capm)')

st.code(f"""
        row beta         : {beta_cov:.5f}
        adj. coefficient : {adjustment_coefficient:.2f}
        adjusted beta    : {beta_cov*adjustment_coefficient:.5f} """)

