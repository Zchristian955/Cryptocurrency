# This app is for educational purpose only. Insights gained is not financial advice. Use at your own risk!
import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from requests import  Request, Session
import json
import time
from streamlit_option_menu import option_menu
import numpy as np
import bitfinex
import datetime
import seaborn as sns
#import matplotlib.finance as mpf


#---------------------------------#
# New feature (make sure to upgrade your streamlit library)
# pip install --upgrade streamlit

#---------------------------------#
# Page layout
## Page expands to full width
st.set_page_config(layout="wide")
#---------------------------------#
# Title



#image = Image.open('cr.jpg')

#st.image(image, width = 700)

st.title('Crypto Price Application')
st.markdown("""
This app retrieves cryptocurrency prices for the top 100 cryptocurrency from the **CoinMarketCap**!
""")

with st.sidebar:
    selected = option_menu("Menu", ["Home","Forcasting","About us"],
        icons=['house', 'play','gear'], default_index=0,orientation="horizontal")





if selected == "Home":
    st.write("**Home page**")











    #---------------------------------#
    # About
    expander_bar = st.expander("About")
    expander_bar.markdown("""
    * **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, BeautifulSoup, requests, json, time
    * **Data source:** [CoinMarketCap](http://coinmarketcap.com).
    """)


    #---------------------------------#
    # Page layout (continued)
    ## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
    col1 = st.sidebar
    col2, col3 = st.columns((10,1))


    #---------------------------------#
    # Sidebar + Main panel
    col1.header('Input Options')

    ## Sidebar - Currency price unit
    currency_price_unit = col1.selectbox('Select currency for price', ('USD','EUR'))


    ######################

    #url= 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'

    #response = session.get(url)
    #pprint.pprint(json.loads(response.text)['data'])

    #print(res)

    #print(json.dumps(res,indent=2))

    @st.cache
    def dit():
        #web scrach
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
            # 'id': '1,2,3,4,5,6,7,8,9,10,12,13,1027',
            # 'symbol': 'BTC,ETH,BNB',
            'convert': 'USD'

        }

        headers = {
            'Accepts': 'application/json',
            'Accept-Encoding': 'gzip',
            'X-CMC_PRO_API_KEY': '54ce78f4-c5a7-48b9-b01c-662f92136a14'
        }
        session = Session()
        session.headers.update(headers)
        response = session.get(url, params=parameters)
        #load the Data
        res = json.loads(response.text)





        dictionary ={'name':[],'symbol':[],'cmc_rank':[],'market_cap':[],'volume_change_24h':[],'percent_change_1h':[],'percent_change_7d':[],'percent_change_30d':[],'percent_change_60d':[],'percent_change_90d':[] ,'price':[],'percent_change_24h':[]}
        for i in res['data']:
            dictionary["name"].append(i['name'])
            dictionary['cmc_rank'].append(i['cmc_rank'])
            dictionary['symbol'].append(i['symbol'])
            dictionary['market_cap'].append(i['quote']['USD']['market_cap'])
            dictionary['volume_change_24h'].append(i['quote']['USD']['volume_change_24h'])
            dictionary['percent_change_1h'].append(i['quote']['USD']['percent_change_1h'])
            dictionary['percent_change_7d'].append(i['quote']['USD']['percent_change_7d'])
            dictionary['percent_change_30d'].append(i['quote']['USD']['percent_change_30d'])
            dictionary['percent_change_60d'].append(i['quote']['USD']['percent_change_60d'])
            dictionary['percent_change_90d'].append(i['quote']['USD']['percent_change_90d'])
            dictionary['percent_change_24h'].append(i['quote']['USD']['percent_change_24h'])
            dictionary['price'].append(i['quote']['USD']['price'])


        return dictionary

    ft = dit()

    df = pd.DataFrame.from_dict(ft)
    #st.table(dt)



    ## Sidebar - Cryptocurrency selections
    sorted_coin = sorted( df['symbol'] )
    selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)

    df_selected_coin = df[ (df['symbol'].isin(selected_coin)) ] # Filtering data

    ## Sidebar - Number of coins to display
    num_coin = col1.slider('Display Top N Coins', 1, 100, 100)
    df_coins = df_selected_coin[:num_coin]



    col2.subheader('Price Data of Selected Cryptocurrency')
    col2.write('Data Dimension: ' + str(df_selected_coin.shape[0]) + ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')

    col2.dataframe(df_coins)






    # Download CSV data
    # https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
    def filedownload(df):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
        href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
        return href

    col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

    #---------------------------------#
    # Preparing data for Bar plot of % Price change
    col2.subheader('Table of % Price Change')
    df_change = pd.concat([df_coins.symbol, df_coins.percent_change_1h, df_coins.percent_change_24h, df_coins.percent_change_7d], axis=1)
    df_change = df_change.set_index('symbol')
    df_change['positive_percent_change_1h'] = df_change['percent_change_1h'] > 0
    df_change['positive_percent_change_24h'] = df_change['percent_change_24h'] > 0
    df_change['positive_percent_change_7d'] = df_change['percent_change_7d'] > 0
    col2.dataframe(df_change)








if selected == "Forcasting":
    def load_data():
        # ccreate api instance of the v2 API

        api_v2 = bitfinex.bitfinex_v1.api_v1()
        # define query parameters

        pair = 'ETHUSD'
        TIMEFRAME = "1h"

        # define the start date
        t_start = datetime.datetime(2020, 9, 1, 0, 0)
        t_start = time.mktime(t_start.timetuple()) * 1000

        # define the end datee

        t_stop = datetime.datetime(2020, 10, 1, 0, 0)
        t_stop = time.mktime(t_stop.timetuple()) * 1000

        # Download OHCL data form API
        # result = api_v2.candles(symbol= pair,interval =TIMEFRAME,limit=1000,
        #                        start=t_start,end=t_stop)
        result = api_v2.candles(symbol=pair, interval=TIMEFRAME, limit=1000,
                                start=t_start, end=t_stop)

        # convert list to data pandas datframe

        names = ['Date', 'ETH_Open', 'ETH_Close', 'ETH_High', 'ETH_Low', 'ETH_Volume']
        df = pd.DataFrame(result, columns=names)
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')

        return df


    data1 = load_data()


    # BTC

    def load_data():
        # ccreate api instance of the v2 API

        api_v2 = bitfinex.api_v2()
        # define query parameters

        pair = 'BTCUSD'
        TIMEFRAME = "1h"

        # define the start date
        t_start = datetime.datetime(2020, 9, 1, 0, 0)
        t_start = time.mktime(t_start.timetuple()) * 1000

        # define the end datee

        t_stop = datetime.datetime(2020, 10, 1, 0, 0)
        t_stop = time.mktime(t_stop.timetuple()) * 1000

        # Download OHCL data form API
        # result = api_v2.candles(symbol= pair,interval =TIMEFRAME,limit=1000,
        #                        start=t_start,end=t_stop)
        result = api_v2.candles(symbol=pair, interval=TIMEFRAME, limit=1000,
                                start=t_start, end=t_stop)

        # convert list to data pandas datframe

        names = ['Date', 'BTC_Open', 'BTC_Close', 'BTC_High', 'BTC_Low', 'BTC_Volume']
        df = pd.DataFrame(result, columns=names)
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')

        return df


    data2 = load_data()


    # DOGE

    def load_data():
        # ccreate api instance of the v2 API

        api_v2 = bitfinex.bitfinex_v2.api_v2()
        # define query parameters

        pair = 'LTCUSD'
        TIMEFRAME = "1h"

        # define the start date
        t_start = datetime.datetime(2020, 9, 1, 0, 0)
        t_start = time.mktime(t_start.timetuple()) * 1000

        # define the end datee

        t_stop = datetime.datetime(2020, 10, 1, 0, 0)
        t_stop = time.mktime(t_stop.timetuple()) * 1000

        # Download OHCL data form API
        # result = api_v2.candles(symbol= pair,interval =TIMEFRAME,limit=1000,
        #                        start=t_start,end=t_stop)
        result = api_v2.candles(symbol=pair, interval=TIMEFRAME, limit=1000,
                                start=t_start, end=t_stop)

        # convert list to data pandas datframe

        names = ['Date', 'LTC_Open', 'LTC_Close', 'LTC_High', 'LTC_Low', 'LTC_Volume']
        df = pd.DataFrame(result, columns=names)
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')

        return df


    data3 = load_data()

    final_data = pd.merge(data1, data2, on=["Date", "Date"])
    final_data1 = pd.merge(final_data, data3, on=["Date", "Date"])
    final_data2 = final_data1.head(25)
    st.dataframe(final_data2)

    #log_return_BTC = np.log(final_data1['BTC_Close']/final_data1['BTC_Close'].shift(1)).dropna()

    final_data3 = final_data1[['Date','BTC_Close','LTC_Close','ETH_Close']]
    final_data3 =final_data3.set_index('Date')
    #st.dataframe(final_data3)



    st.header('Financial Plots')
    st.header('**BTC**')
    final_data1 = final_data1.set_index('Date')
    final_data1[['BTC_Open', 'BTC_Close', 'BTC_High', 'BTC_Low']].plot(figsize=(8, 5))
    st.pyplot()

    st.header('**ETH**')
    #final_data1 = final_data1.set_index('Date')
    final_data1[['ETH_Open', 'ETH_Close', 'ETH_High', 'ETH_Low']].plot(figsize=(8, 5))
    st.pyplot()

    st.header('**LTC**')
    #final_data1 = final_data1.set_index('Date')
    final_data1[['LTC_Open', 'LTC_Close', 'LTC_High', 'LTC_Low']].plot(figsize=(8, 5))
    st.pyplot()



    st.header('***Daily volatility***')
    st.markdown('''Volatility is a statistical measure of the dispersion of returns for a given security or market index. In most cases, the higher the volatility, the riskier the security. Volatility is often measured as either the standard deviation or variance between returns from that same security or market index.
    ''')
    width = st.sidebar.slider("plot width", 0.1, 25., 3.)
    height = st.sidebar.slider("plot height", 0.1, 25., 1.)
    fig, ax = plt.subplots(figsize=(width, height))
    daily_vol = final_data3.pct_change().apply(lambda x: np.log(1 + x)).std()*100
    daily_vol.plot(kind='bar')
    #final_data3 =pd.DataFrame(final_data3,columns='volatility')
    #st.dataframe(final_data3)
    #ax.bar(langs, students)
    #plt.plot
    st.pyplot(plt)

    st.header('***Annual volatility***')
    final_data4 = final_data3.pct_change().apply(lambda x: np.log(1 + x)).std()*np.sqrt(252)
    final_data4 = final_data4*100
    final_data4 = pd.DataFrame(final_data4)
    final_data4 = final_data4.rename(columns={0: 'Annual_Volatlity'})
    #final_data4['Annual_Volatlity'] = final_data4[0]
    #final_data = final_data4['Annual_Volatlity']
    #final_data4.plot(kind ='bar')
    st.dataframe(final_data4)
    #width = st.sidebar.slider("plot width", 0.1, 25., 3.)
    #height = st.sidebar.slider("plot height", 0.1, 25., 1.)
    #fig, ax = plt.subplots(figsize=(width, height))
    #final_data3 = final_data3.pct_change().apply(lambda x: np.log(1 + x)).std().apply(lambda x: x.np.sqrt(252)).plot(kind='bar')
    #st.pyplot(plt)


    st.header ("Trend of the volatility  each 20 Hours")
    final_data5 = final_data3.pct_change().apply(lambda x: np.log(1 + x))
    day= 20
    vol = final_data5.rolling(window=day).std()*np.sqrt(day)
    vol.plot()
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()





    st.header('Correlation coefficient with price ')
    cor = final_data1.corr(method="pearson")
    st.dataframe(cor)





    st.header('Correlation map ')
    plt.figure(figsize=(16, 6))
    heatmap = sns.heatmap(cor, vmin=-1, vmax=1, annot=True)
    # Give a title to the heatmap. Pad defines the distance of the title from the top of the heatmap.
    heatmap.set_title('Correlation Heatmap Price', fontdict={'fontsize': 20}, pad=20)
    #sns.heatmap(cor)
    st.pyplot()



    st.header('Compute coorelation with crypto price')
    ist_select = st.selectbox("1st Crypto currency", final_data1.columns)
    iind_select = st.selectbox("2st Crypto currency", final_data1.columns)
    #corrr =
    f = final_data1[ist_select]
    g = final_data1[iind_select]
    corr = f.corr(g)

    st.write("#### The correlation among them is :", corr)


    #st.dataframe(f)

    st.header('Volatility of crypto currency')
    day_vol = final_data1.pct_change().apply(lambda x: np.log(1 + x)).std()*100
    #st.selectbox("Volatility of crypto currency")
    #st.dataframe(day_vol)
    day5 = pd.DataFrame(day_vol)
    day5 = day5.rename(columns={0: 'Daily Volatlity', ' ':'Crypto'})
    #df_new = df.rename(columns={'A': 'Col_1'}, index={'ONE': 'Row_1'})
    st.dataframe(day5)


    st.header(":mailbox: Get me in touch! ")


    contact_form = """
    <form action="https://formsubmit.co/codingisfun.testuser@email.com" method="POST">
         <input type="text" name="name" required>
         <input type="email" name="email" required>
         <button type="submit">Send</button>
    </form>
    """


    st.markdown(contact_form,unsafe_allow_html=True)


if selected =="About us":
    st.info("Information")
    st.info("Goal")




