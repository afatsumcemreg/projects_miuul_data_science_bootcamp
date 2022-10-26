# understanding the data

# import the libraries
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# import the dataset
df_ = pd.read_excel('datasets/online_retail_II.xlsx', sheet_name='Year 2010-2011')
df = df_.copy()
df.columns = [col.lower() for col in df.columns]
df.head()

# check dataframe
def check_dataframe(dataframe, head=10):
    print(dataframe.head(head))
    print(dataframe.tail(head))
    print(dataframe.shape)
    print(dataframe.columns)
    print(dataframe.info())
    print(dataframe.isnull().values.any())
    print(dataframe.isnull().sum())
    print(dataframe.describe().T)

check_dataframe(df)

# grabing the variables categorical, numerical, and cardinal
def grab_col_names(dataframe, cat_th=10, car_th=20):
    """
    cat_cols, num_cols, cat_but_car = grab_col_names(df)
    """
    # katogorical variables
    cat_cols = [col for col in dataframe.columns if dataframe[col].dtypes == 'O']
    num_but_cat = [col for col in dataframe.columns if
                   dataframe[col].nunique() < cat_th and dataframe[col].dtypes != 'O']
    cat_but_car = [col for col in dataframe.columns if
                   dataframe[col].nunique() > car_th and dataframe[col].dtypes == 'O']
    cat_cols = cat_cols + num_but_cat
    cat_cols = [col for col in cat_cols if col not in cat_but_car]

    # numerical variables
    num_cols = [col for col in dataframe.columns if dataframe[col].dtypes not in ['bool', 'category', 'object']]
    num_cols = [col for col in num_cols if col not in num_but_cat]

    # reporting section
    print(f'Observations: {dataframe.shape[0]}')
    print(f'Variables: {dataframe.shape[1]}')
    print(f'cat_cols: {len(cat_cols)}')
    print(f'num_cols: {len(num_cols)}')
    print(f'cat_but_car: {len(cat_but_car)}')
    print(f'num_but_cat: {len(num_but_cat)}')

    # hesaplanan degerleri tutma
    return cat_cols, num_cols, cat_but_car

cat_cols, num_cols, cat_but_car = grab_col_names(df)

# examine the cardinal variables
df['country'].value_counts()
df['stockcode'].value_counts()
df['description'].value_counts()
df.groupby('description').agg(
    {'quantity': 'sum',
    'price': 'sum',
    'invoicedate': 'count',
    'stockcode': 'count',
    'country': 'count'
    }).sort_values('quantity', ascending=False)

# get the total price
df['total_price'] = df['price'] * df['quantity']

# examine the invoice with total price
df.groupby('invoice').agg({'total_price': 'sum'}).sort_values('total_price', ascending=False)

# data preparation

# observ the missing data
df.isnull().sum()

# drop them
df.dropna(inplace=True)

# find the observations with the invoices with 'C'
df[df['invoice'].str.contains('C', na=False)]

# delete the observations with the invoices with 'C'
df = df[~df['invoice'].str.contains('C', na=False)]
df.shape

# calculation of rfm metrics (recency, frequency, monetary)

# determine the last date in the variable invoicedate
df['invoicedate'].max()

# add 2 days to the last day of the variable invoicedate
analysis_date = dt.datetime(2011, 12, 11)

df.groupby('customer id').agg({
    'invoicedate': lambda x: (analysis_date - x.max()).days,
    'invoice': lambda x: x.nunique(),
    'total_price': lambda x: x.sum()
}).head()

# Create a new datafrema named 'rfm'
rfm = df.groupby('customer id').agg({
    'invoicedate': lambda x: (analysis_date - x.max()).days,
    'invoice': lambda x: x.nunique(),
    'total_price': lambda x: x.sum()
})
rfm.head()

# change the column names with recency, frequency and monetary
rfm.columns = ['recency', 'frequency', 'monetary']

# monetary must not be lower than and equal to 0
rfm = rfm[rfm['monetary'] > 0]

# calculation of rfm scores
rfm['recency_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm['monetary_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
rfm['frequency_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])

# determinin rf and rfm scores
rfm['rf_score'] = rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str)
rfm['rfm_score'] = rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str)

# creating rfm segments
segment_map = {r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_risk',
    r'[1-2]5': 'cant_loose_them',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'}

rfm['segments'] = rfm['rf_score'].replace(segment_map, regex=True)

# examine the mean and count values of the scores according to segments
rfm.groupby('segments').agg(
    {'recency': ['mean', 'count'],
    'frequency': ['mean', 'count'],
    'monetary': ['mean', 'count']})

# reaching to the indexes of new_customers, cant_loose_them, and need_attention
rfm[rfm['segments'] == 'new_customers'].index
rfm[rfm['segments'] == 'cant_loose_them'].index
rfm[rfm['segments'] == 'need_attention'].index

new_df = pd.DataFrame()
new_df['new_customer_id'] = rfm[rfm['segments'] == 'new_customers'].index
new_df['new_customer_id'] = new_df['new_customer_id'].astype(int)

# get the final format of the new_df and rfm as csv file
# new_df.to_csv('new_customers.csv')
# rfm.to_csv('rfm.csv')

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