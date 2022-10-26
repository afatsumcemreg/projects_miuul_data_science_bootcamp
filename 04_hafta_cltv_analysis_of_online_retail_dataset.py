###############################################
# Customer Lifetime Value (CLTV) of Online Retail Dataset
###############################################

# data preparation

# import libraries
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# read dataset

df_ = pd.read_excel('datasets/online_retail_II.xlsx', sheet_name='Year 2009-2010')
df = df_.copy()
df.columns = [col.lower() for col in df.columns]
df.head()

# delete the observations with 'C' in the invoice variable
df = df[~df['invoice'].str.contains('C', na=False)]

# show the description statistics
df.describe().T

# there are negative values in the variables prices and quantity. they must be removed from the dataset
df = df[df['quantity'] > 0]

# find the missing data
df.isnull().sum()

# the missing data must be removed from the dataset
df.dropna(inplace=True)

# the variable price cant be zero
df = df[df['price'] > 0]
df.describe().T
df.shape

# get the total price
df['total_price'] = df['price'] * df['quantity']

# conver the dataset to the cltv format
cltv = df.groupby('customer id').agg({
    'invoice': lambda x: x.nunique(),
    'quantity': lambda x: x.sum(),
    'total_price': lambda x: x.sum()
})

# change the names of the variables
cltv.columns = ['total_transaction', 'total_unit', 'total_price']
cltv.shape  # now, the observations are unique. each obervation represents a different customer

# get the average order value (total_price / total_transaction)
cltv['average_order_value'] = cltv['total_price'] / cltv['total_transaction']

# get the purchase frequency (total_transaction / total number of customers)
cltv['purchase_frequency'] = cltv['total_transaction'] / cltv.shape[0]

# get the repeat rate and churn rate 
repeat_rate = cltv[cltv['total_transaction'] > 1].shape[0] / cltv.shape[0]
churn_rate = 1- repeat_rate

# get the profir margin (total_price * 0.1)
cltv['profit_margin'] = cltv['total_price'] * 0.1

# get the customer value (average_order_value * purchase_frequency)
cltv['customer_value'] = cltv['average_order_value'] * cltv['purchase_frequency']

# get the cltv value
cltv['cltv'] = (cltv['customer_value'] / churn_rate) * cltv['profit_margin']

# sort the cltv values in ascending order
cltv.sort_values(by='cltv', ascending=False)

# get the descriptive statistics to interpret tha data again
cltv.describe().T

# creating the segements
cltv['segment'] = pd.qcut(cltv['cltv'], 4, labels=['D', 'C', 'B', 'A'])
cltv.sort_values(by='cltv', ascending=False)

# analys the segement in terms of mean, count, and sum
cltv.groupby('segment').agg({'count', 'mean', 'sum'})

# save the final file as a csv file
cltv.to_csv('cltv.csv')

# functionalization of all process made
def create_cltv(dataframe, profit=0.10, save=False):
    # data preparation
    dataframe = dataframe[~dataframe['invoice'].str.contains('C', na=False)]
    dataframe = dataframe[dataframe['quantity'] > 0]
    dataframe = dataframe[dataframe['price'] > 0]
    dataframe.dropna(inplace=True)
    dataframe['total_price'] = dataframe['quantity'] * dataframe['price']
    cltv = dataframe.groupby('customer id').agg({
        'invoice': lambda x: x.nunique(),
        'quantity': lambda x: x.sum(),
        'total_price': lambda x: x.sum()
    })
    cltv.columns = ['total_transaction', 'total_unit', 'total_price']

    # average order value
    cltv['average_order_value'] = cltv['total_price'] / cltv['total_transaction']

    # purchase_frequency
    cltv['purchase_frequency'] = cltv['total_transaction'] / cltv.shape[0]

    # repeat_rate & churn_rate
    repeat_rate = cltv[cltv['total_transaction'] > 1].shape[0] / cltv.shape[0]
    churn_rate  = 1 - repeat_rate

    # profit margin
    cltv['profit_margin'] = cltv['total_price'] * profit

    # customer value
    cltv['customer_value'] = cltv['average_order_value'] * cltv['purchase_frequency']

    # cltv value
    cltv['cltv'] = (cltv['customer_value'] / churn_rate) * cltv['profit_margin']

    # creating segments
    cltv['segments'] = pd.qcut(cltv['cltv'], 4, labels=['D', 'C', 'B', 'A'])

    if save:
        cltv.to_csv('cltv.csv')

    return cltv

# call the dataframe again
df = df_.copy()
df.columns = [col.lower() for col in df.columns]
create_cltv(df, save=True)


