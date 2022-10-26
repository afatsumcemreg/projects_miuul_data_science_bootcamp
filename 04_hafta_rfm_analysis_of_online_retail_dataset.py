# Understanding the data
# Import the libraries
import pandas as pd
from helpers import eda
import datetime as dt
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# import the dateset
df_ = pd.read_excel('datasets/online_retail_II.xlsx', sheet_name='Year 2009-2010')
df_.columns = [col.lower() for col in df_.columns]
df = df_.copy()
df.head()

eda.check_df(df)
cat_cols, num_cols, cat_but_car = eda.grab_col_names(df)
num_cols = [col for col in num_cols if col not in ['InvoiceDate','Customer ID']]

# get the unique number of product
df['description'].nunique()

# get the frequence of each product
df['description'].value_counts()

# get how many each product were sold in total
df.groupby('description').agg({'quantity': 'sum'}).sort_values(by='quantity', ascending=False).head()

# get the unique number of invoices
df['invoice'].nunique()

# create a new variable named 'total_price', hich gives the total price of each product
df['total_price'] = df['quantity'] * df['price']
df.sort_values(by='total_price', ascending=False).head()

# get the total price paid per each invoice 
df.groupby('invoice').agg({'total_price': 'sum'}).head().sort_values(by='total_price', ascending=False)

# preparation of the dataset

# get the missing data
df.isnull().sum()

# delete the missing data
df.dropna(inplace=True)

# delete the null values
df.dropna(inplace=True)

# get the invoices containing the 'C', which refers the returns
df[df['invoice'].str.contains('C', na=False)]

# delete the invoices containing the 'C', which refers the returns and assign it to the dataframe
df = df[~df['invoice'].str.contains('C', na=False)]
df.shape

# calculation of rfm metrics (recency, frequency, and monetary)
    # recency = date of analysis - purchase date of the relevant customer
    # frequency = customer's total number of purchases
    # monetary = total monetary value as a result of the customer's total purchases

# get the last invoice date in the dataset
df['invoicedate'].max() # Timestamp('2010-12-09 20:01:00')

# adding 2 days to the calculated last data
today_date = dt.datetime(2010, 12, 11)

# get the type of the today_data
type(today_date)    # <class 'datetime.datetime'>

# the base of the rfm analysis is a simple pandas operation
# in the 'customer id' breakdown, get a groupby() proces and calculate the r, f, and m values
rfm = df.groupby('customer id').agg({
    'invoicedate': lambda x: (today_date - x.max()).days,
    'invoice': lambda x: x.nunique(),
    'total_price': lambda x: x.sum()})
rfm.head()

# change the column names
rfm.columns = ['recency', 'frequency', 'monetary']

# get the descriptive statistics
rfm.describe().T
rfm.shape

# delete the null values from the monetary values since its value can not be null
rfm = rfm[rfm['monetary'] > 0]

# calculation the rfm scores

# convert the recency values to scores
rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
# normally, the the best recency value is one, but after converting the best recency score is 5

# convert the monetary values to scores
rfm['monetary_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

# convert the frequency values to scores
rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
# when rank(method='first') is not used, it gives a ValueError. because, there are many repeated frequence values
# and when ordering small to big, the values in the quantiles were the same. to solve this, rank method was used.
# when this method was used, assign the first seen value to the first class

# after this stage, by using the R and F values, the scores can be formed.
rfm['rfm_score'] = rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str)
rfm[rfm['rfm_score'] == '55'].head()   # champions group
rfm[rfm['rfm_score'] == '11'].head()   # hibernating group

# creating the rfm segments

# rfm nomenclatures
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_risk',
    r'[1-2]5': 'cant_loose_them',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising', 
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

# to add the nomenclatures in the dataframe, use replace() method
rfm['segments'] = rfm['rfm_score'].replace(seg_map, regex=True)

# reaching the average scores and counts of recency, frequency, monetary in those classes
rfm[['segments', 'recency', 'frequency', 'monetary']].groupby('segments').agg(['mean', 'count'])

# the manager can want the classes 'need_attention', 'cant_loose_them', and 'new_customers'
rfm[rfm['segments'] == 'need_attention'].head()
rfm[rfm['segments'] == 'cant_loose_them'].head()
rfm[rfm['segments'] == 'new_customers'].head()
rfm[rfm['segments'] == 'need_attention'].index
rfm[rfm['segments'] == 'cant_loose_them'].index
rfm[rfm['segments'] == 'new_customers'].index
# rfm[rfm['segments'] == 'new_customers'].to_csv('new_customers.csv')

# sending the customer id data to the relevant department
new_df = pd.DataFrame()
new_df['new_customer_id'] = rfm[rfm['segments'] == 'new_customers'].index
new_df['new_customer_id'] = new_df['new_customer_id'].astype(int)   # to yield clearer customer ids 

# saving the relevant output as a csv file
new_df.to_csv('new_customers.csv')

# saving the rfm dataset as a csv file
rfm.to_csv('rfm.csv')

# functionalization of all process
def create_rfm(dataframe, csv=False):
    # Data preparation
    dataframe['total_price'] = dataframe['quantity'] * dataframe['price']
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe['invoice'].str.contains('C', na=False)]

    # calculation of rfm metrics
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('customer id').agg({
        'invoicedate' : lambda date: (today_date - date.max()).days,
        'invoice' : lambda num: num.nunique(),
        'total_price': lambda total_price: total_price.sum()
    })
    rfm.columns = ['recency', 'frequency', 'monetary']
    rfm = rfm[rfm['monetary'] > 0]

    # calculation of rfm scores
    rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['monetary_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    # getting rfm scores
    rfm['rfm_score'] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))

    # nomenclatures of the segments
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose_them',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising', 
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segments'] = rfm['rfm_score'].replace(seg_map, regex=True)
    rfm = rfm[['recency', 'frequency', 'monetary', 'segments']]
    rfm.index = rfm.index.astype(int)

    # saving a separate file the last dataframe
    if csv:
        rfm.to_csv('rfm.csv')
    
    return rfm

# call the dataset again
df = df_.copy()
df.columns = [col.lower() for col in df.columns]
rfm_new = create_rfm(df)     # can not create the csv file
rfm_new = create_rfm(df, csv=True) # create the csv file
rfm_new.head() 


