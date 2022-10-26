##########################################################################
# CLTV Prediction with BG-NBD and GG Models using Online Retail Dataset
##########################################################################

# import libraries
import datetime as dt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from lifetimes import GammaGammaFitter, BetaGeoFitter
from lifetimes.plotting import plot_period_transactions
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# supressing the aoutliers
def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit

def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = round(low_limit, 0)
    dataframe.loc[(dataframe[variable] > up_limit), variable] = round(up_limit, 0)

# import dataset
df_ = pd.read_excel('datasets/online_retail_II.xlsx', 
                    sheet_name='Year 2010-2011')
df = df_.copy()
df.columns = [col.lower() for col in df.columns]
df.head()
df.isnull().sum()

# data preparation

# since there are missing data, they can be removed from the dataset
df.dropna(inplace=True)
df.describe().T
df.shape

# in this dataset, the returned products are marked with 'C' in the variable invoice. They must be removed from the dataset
df = df[~df['invoice'].str.contains('C', na=False)]

# the variables price and quantitiy must be bigger than 0
df = df[(df['quantity'] > 0)]
df = df[(df['price'] > 0)]

# before supressing the outliers with thresholds, check the outlier using box plot
sns.boxplot(x = df['price'])
plt.show(block=True)
sns.boxplot(x = df['quantity'])
plt.show(block=True)

# supressing the outliers
replace_with_thresholds(df, 'quantity')
replace_with_thresholds(df, 'price')

# after supressing the outliers with thresholds, check the outlier using box plot
sns.boxplot(x = df['price'])
plt.show(block=True)
sns.boxplot(x = df['quantity'])
plt.show(block=True)

# create the variable 'total_price'
df['total_price'] = df['quantity'] * df['price']

# define the analysis day for 2 days after
df['invoicedate'].max()
today_date = dt.datetime(2011, 12, 11)

# preparation of lifetime data structure
# recency, tenure, frequency and monetary

cltv_df = df.groupby('customer id').agg(
    {'invoicedate': [lambda invoicedate: (invoicedate.max() - invoicedate.min()).days,
        lambda invoicedate: (today_date - invoicedate.min()).days],
    'invoice': lambda invoice: invoice.nunique(),
    'total_price': lambda total_price: total_price.sum()})

# there is hierarchical index problem in the output.it must be solved
cltv_df.columns = cltv_df.columns.droplevel(0)

# assign the varibale names as recency, tenure, frequency and monetary
cltv_df.columns = ['recency', 'tenure', 'frequency', 'monetary']

# converting the data to the type requested by the model
cltv_df = cltv_df[(cltv_df['frequency'] > 1)]
cltv_df['monetary'] = cltv_df['monetary'] / cltv_df['frequency']
cltv_df['recency'] = cltv_df['recency'] / 7
cltv_df['tenure'] = cltv_df['tenure'] / 7

# establishing bg-nbd model
bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(cltv_df['frequency'], cltv_df['recency'], cltv_df['tenure'])

# 10 customers with the most expected purchases in a week
bgf.conditional_expected_number_of_purchases_up_to_time(1, 
    cltv_df['frequency'], 
    cltv_df['recency'], 
    cltv_df['tenure']).sort_values(ascending=False).head(10)

bgf.predict(1, 
    cltv_df['frequency'], 
    cltv_df['recency'], 
    cltv_df['tenure']).sort_values(ascending=False).head(10)

# add the expected purchases in a week into the dataframe cltv_df
cltv_df['expected_purch_1_week'] = bgf.predict(1, 
    cltv_df['frequency'], 
    cltv_df['recency'], 
    cltv_df['tenure'])

# 10 customers with the most expected purchases in a month
bgf.predict(1 * 4, 
    cltv_df['frequency'], 
    cltv_df['recency'], 
    cltv_df['tenure']).sort_values(ascending=False).head(10)

cltv_df['expected_purch_1_month'] = bgf.predict(1 * 4, 
    cltv_df['frequency'], 
    cltv_df['recency'], 
    cltv_df['tenure'])

# Reaching the number of sales expected by the company in a 3-month period
bgf.predict(4 * 3, 
    cltv_df['frequency'], 
    cltv_df['recency'], 
    cltv_df['tenure']).sum()

cltv_df['expected_purch_3_month'] = bgf.predict(3 * 4, 
    cltv_df['frequency'], 
    cltv_df['recency'], 
    cltv_df['tenure'])

# evaluating the succes of the prediction results
plot_period_transactions(bgf)
plt.show(block=True)

# establishing gamma gamma model
ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(cltv_df['frequency'], cltv_df['monetary'])

# reaching the conditional_expected_averege profit values
ggf.conditional_expected_average_profit(
    cltv_df['frequency'], cltv_df['monetary']).head()

# reaching the conditional_expected_averege profit values in the ascending order
ggf.conditional_expected_average_profit(
    cltv_df['frequency'], 
    cltv_df['monetary']).sort_values(ascending=False).head()

# saving the conditional_expected_averege profit values in the ascending order into the dataframe cltv_df
cltv_df['expected_average_profit'] = ggf.conditional_expected_average_profit(
    cltv_df['frequency'], 
    cltv_df['monetary'])

# Calculation of cltv using bg-nbd and gg models
cltv = ggf.customer_lifetime_value(bgf, 
                                cltv_df['frequency'], 
                                cltv_df['recency'], 
                                cltv_df['tenure'], 
                                cltv_df['monetary'], 
                                time = 3, # 3 months
                                freq = 'W',  # frequency iformation of tenure in weekly
                                discount_rate = 0.01)

cltv.head()

# there is an index problem in the output yielded.
cltv = cltv.reset_index()

# creating final dataframe
cltv_final = cltv_df.merge(cltv, on ='customer id', how='left')
cltv_final.sort_values(by='clv', ascending=False).head()

# creating segements according to 'clv'
cltv_final['segment'] = pd.qcut(cltv_final['clv'], 4, labels=['D', 'C', 'B', 'A'])
cltv_final.sort_values(by='clv', ascending=False).head(50)

def decision_process(dataframe, target, variable):
    print(dataframe.groupby(target).agg({variable: ['mean', 'count', 'sum']}))

num_cols = [col for col in cltv_final.columns if cltv_final[col].dtypes not in ['bool', 'category', 'object']]
num_cols = [col for col in num_cols if 'customer id' not in col]
for col in num_cols:
    decision_process(cltv_final, 'segment', col)

# functionalization of all process
def create_cltv_prediction(dataframe, month=3):
    # data preparation
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["invoice"].str.contains("C", na=False)]
    dataframe = dataframe[dataframe["quantity"] > 0]
    dataframe = dataframe[dataframe["price"] > 0]
    replace_with_thresholds(dataframe, "quantity")
    replace_with_thresholds(dataframe, "price")
    dataframe["total_price"] = dataframe["quantity"] * dataframe["price"]
    today_date = dt.datetime(2011, 12, 11)

    cltv_df = dataframe.groupby('customer id').agg(
        {'invoicedate': [lambda invoicedate: (invoicedate.max() - invoicedate.min()).days,
                         lambda invoicedate: (today_date - invoicedate.min()).days],
         'invoice': lambda invoice: invoice.nunique(),
         'total_price': lambda total_price: total_price.sum()})

    cltv_df.columns = cltv_df.columns.droplevel(0)
    cltv_df.columns = ['recency', 'T', 'frequency', 'monetary']
    cltv_df["monetary"] = cltv_df["monetary"] / cltv_df["frequency"]
    cltv_df = cltv_df[(cltv_df['frequency'] > 1)]
    cltv_df["recency"] = cltv_df["recency"] / 7
    cltv_df["T"] = cltv_df["T"] / 7

    # establishement of bg-nbd model
    bgf = BetaGeoFitter(penalizer_coef=0.001)
    bgf.fit(cltv_df['frequency'],
            cltv_df['recency'],
            cltv_df['T'])

    cltv_df["expected_purc_1_week"] = bgf.predict(1,
                                                  cltv_df['frequency'],
                                                  cltv_df['recency'],
                                                  cltv_df['T'])

    cltv_df["expected_purc_1_month"] = bgf.predict(4,
                                                   cltv_df['frequency'],
                                                   cltv_df['recency'],
                                                   cltv_df['T'])

    cltv_df["expected_purc_3_month"] = bgf.predict(12,
                                                   cltv_df['frequency'],
                                                   cltv_df['recency'],
                                                   cltv_df['T'])

    # establishement of gamma gamma model
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(cltv_df['frequency'], cltv_df['monetary'])
    cltv_df["expected_average_profit"] = ggf.conditional_expected_average_profit(cltv_df['frequency'],
                                                                                 cltv_df['monetary'])

    # calculation of cltv using bg-nbd and gg models
    cltv = ggf.customer_lifetime_value(bgf,
                                       cltv_df['frequency'],
                                       cltv_df['recency'],
                                       cltv_df['T'],
                                       cltv_df['monetary'],
                                       time=month,  # 3 aylık
                                       freq="W",  # T'nin frekans bilgisi.
                                       discount_rate=0.01)

    cltv = cltv.reset_index()
    cltv_final = cltv_df.merge(cltv, on="customer id", how="left")

    # creating the segments
    cltv_final["segment"] = pd.qcut(cltv_final["clv"], 4, labels=["D", "C", "B", "A"])

    return cltv_final


df = df_.copy()
df.columns = [col.lower() for col in df.columns]
cltv_final2 = create_cltv_prediction(df)
cltv_final2.to_csv('cltv_prediction.csv')
