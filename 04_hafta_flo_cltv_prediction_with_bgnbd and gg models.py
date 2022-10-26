##########################################################
# CLTV Prediction with BG-NBD and Gamma-Gamma
##########################################################

# business problem
########################################################
"""
FLO wants to set a roadmap for sales and marketing activities. 
In order for the company to make a medium-long-term plan, 
it is necessary to estimate the potential value that existing customers 
will provide to the company in the future.
"""

# dataset story
########################################################
"""
The dataset consists of the information obtained from the past shopping 
behavior of customers who made their last purchases from Flo as OmniChannel 
(both online and offline shopper) between 2020 and 2021.

master_id:	Eşsiz müşteri numarası
order_channel:	Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile)
last_order_channel:	En son alışverişin yapıldığı kanal
first_order_date:	Müşterinin yaptığı ilk alışveriş tarihi
last_order_date:	Müşterinin yaptığı son alışveriş tarihi
last_order_date_online:	Müşterinin online platformda yaptığı son alışveriş tarihi
last_order_date_offline:	Müşterinin offline platformda yaptığı son alışveriş tarihi
order_num_total_ever_online:	Müşterinin online platformda yaptığı toplam alışveriş sayısı
order_num_total_ever_offline:	Müşterinin offline'da yaptığı toplam alışveriş sayısı
customer_value_total_ever_offline:	Müşterinin offline alışverişlerinde ödediği toplam ücret
customer_value_total_ever_online:	Müşterinin online alışverişlerinde ödediği toplam ücret
interested_in_categories_12:	Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi

"""

# Task 1: Understanding and Preparing the Data

# import libraries
import pandas as pd
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
from lifetimes import GammaGammaFitter, BetaGeoFitter
from lifetimes.plotting import plot_period_transactions
from sklearn.preprocessing import MinMaxScaler

# making some adjsutments
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# Task 1. Data Preparation

# step 1: reading the dataset
df_ = pd.read_csv('datasets/flo_rfm_analizi_dataset.csv')
df_.columns = [col.lower() for col in df_.columns]
df = df_.copy()
df.head()

# step 2: Step 2: Define the outlier_thresholds and replace_with_thresholds functions needed to suppress outliers. 
# Note: When calculating cltv, frequency values must be integers. Therefore, round the lower and upper limits with round().

# defining a function that grabs outlier
def outlier_thresholds(dataframe, variable, q1=0.05, q3=0.95):
    quartile1 = dataframe[variable].quantile(q1)
    quartile3 = dataframe[variable].quantile(q3)
    interquartile_range = quartile3 - quartile1
    up_level = quartile3 + 1.5 * interquartile_range
    low_level = quartile1 - 1.5 * interquartile_range
    up_level = round(up_level)
    low_level = round(low_level)

    return low_level, up_level

# defining a function that suppresses outliers
def replace_with_thresholds(dataframe, variable):
    low_level, up_level = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_level, variable)] = low_level
    dataframe.loc[(dataframe[variable] > up_level), variable] = up_level

df.describe().T

# Step 3: If the variables "order_num_total_ever_online", "order_num_total_ever_offline", 
# "customer_value_total_ever_offline", "customer_value_total_ever_online" have outliers, suppress them
variables = [col for col in df.columns if 'ever' in col]
for col in variables:
    replace_with_thresholds(df, col)

# Step 4: Omnichannel means that customers shop from both online and offline platforms.
# Create new variables for each customer's total purchases and spending
df['total_price'] = df['customer_value_total_ever_offline'] * df['customer_value_total_ever_online']
df['total_order'] = df['order_num_total_ever_online'] + df['order_num_total_ever_offline']
df.describe().T

# Step 5: Examine the variable types. Change the type of variables that express date to date.
df.dtypes
col_names = [col for col in df.columns if 'date' in col]    # selecting the columns including 'date'
col_names = df.columns[df.columns.str.contains('date')]     # selecting the columns including 'date'
# first solution
    # for col in col_names:
    #     df[col] = pd.to_datetime(df[col])

# second solution
df[col_names] = df[col_names].apply(pd.to_datetime)

# Task 2: Creating the CLTV Data Structure

# step 1: take 2 days after the last shopping date in the data set as the analysis date
df['last_order_date'].max()
today_date = dt.datetime(2021, 6, 1)
df['order_date_difference'] = (df['last_order_date'] - df['first_order_date']).dt.days

# Step 2: Create a new cltv dataframe with customer_id, recency_cltv_weekly, T_weekly, 
# frequency and monetary_cltv_avg values.
# Monetary value will be expressed as the average value per purchase, and recency and 
# tenure values will be expressed in weekly terms.

# first solution¨
df['order_date_difference'] = (df['last_order_date'] - df['first_order_date']).dt.days
cltv_df = df.groupby('master_id').agg({
     'order_date_difference': lambda order_date_difference: order_date_difference / 7,
     'first_order_date': lambda first_order_date: ((today_date - first_order_date).dt.days) / 7,
     'total_order' : lambda total_order: total_order,
     'total_price': lambda total_price: total_price})
cltv_df['total_price'] = cltv_df['total_price'] / cltv_df['total_order']
cltv_df.columns = ['recency_cltv_weekly', 't_weekly', 'frequency', 'monetary_cltv_avg']
cltv_df = cltv_df[(cltv_df['frequency'] > 1)]

# second solution
cltv_df = pd.DataFrame()
cltv_df["customer_id"] = df["master_id"]
cltv_df["recency_cltv_weekly"] = (df["last_order_date"] - df["first_order_date"]).dt.days
cltv_df['t_weekly'] = (today_date - df["first_order_date"]).dt.days
cltv_df['frequency'] = df["total_order"]

cltv_df["monetary_cltv_avg"] = df["total_price"] / cltv_df["frequency"]
cltv_df = cltv_df[(cltv_df['frequency'] > 1)]
cltv_df["recency_cltv_weekly"] = cltv_df["recency_cltv_weekly"] / 7
cltv_df["t_weekly"] = cltv_df["t_weekly"] / 7

# Task 3: Establishment of BG/NBD, Gamma-Gamma Models and Calculation of CLTV

# Step 1: Fit the BG/NBD model
bgf = BetaGeoFitter(penalizer_coef=0.001).fit(
    cltv_df['frequency'], 
    cltv_df['recency_cltv_weekly'], 
    cltv_df['t_weekly'])

# output: <lifetimes.BetaGeoFitter: fitted with 19945 subjects, a: 0.00, alpha: 80.49, b: 0.00, r: 3.83>

# Estimate expected purchases from customers in 3 months and add exp_sales_3_month to cltv dataframe
cltv_df['expected_purc_3_month'] = bgf.conditional_expected_number_of_purchases_up_to_time(12,
    cltv_df['frequency'],
    cltv_df['recency_cltv_weekly'],
    cltv_df['t_weekly'])

# Estimate expected purchases from customers in 6 months and add exp_sales_6_month to cltv dataframe
cltv_df['expected_purc_6_month'] = bgf.conditional_expected_number_of_purchases_up_to_time(24,
    cltv_df['frequency'],
    cltv_df['recency_cltv_weekly'],
    cltv_df['t_weekly'])

plot_period_transactions(bgf)
plt.show(block=True)

# Step 2: Fit the Gamma-Gamma model
ggf = GammaGammaFitter(penalizer_coef=0.01).fit(cltv_df['frequency'], cltv_df['monetary_cltv_avg'])
# output: <lifetimes.GammaGammaFitter: fitted with 19945 subjects, p: 2.69, q: 0.14, v: 2.63>

# Estimate the average value of the customers and add it to the cltv dataframe as exp_average_value
cltv_df['exp_average_value'] = ggf.conditional_expected_average_profit(cltv_df['frequency'], cltv_df['monetary_cltv_avg'])
sns.scatterplot(x = cltv_df['monetary_cltv_avg'], y=cltv_df['exp_average_value'])
plt.show(block=True)

# Step 3: Calculate 6 months CLTV and add it to the dataframe with the name cltv
cltv_df['cltv'] = ggf.customer_lifetime_value(bgf, cltv_df['frequency'], cltv_df['recency_cltv_weekly'], cltv_df['t_weekly'],
cltv_df['monetary_cltv_avg'], time=6, freq = 'W', discount_rate=0.01)

# • Observe the 20 people with the highest cltv value.
cltv_df.sort_values('cltv', ascending=False).head(20)

# Task 4: Creating Segments by CLTV Value

# Step 1: Divide all your customers into 4 groups (segments) according to 6-month CLTV and add the group names to the dataset.
cltv_df['segment'] = pd.qcut(cltv_df['cltv'], 4, labels=['D', 'C', 'B', 'A'])
cltv_df.head()

# Step 2: Make short 6-month action suggestions to the management for 2 groups you will choose from among 4 groups.
def taking_action(dataframe, target, variable):
    print(dataframe.groupby(target).agg({variable: ['mean', 'count', 'sum']}))

num_cols = [col for col in cltv_df.columns if cltv_df[col].dtypes not in ['bool', 'category', 'object']]
for col in num_cols:
    taking_action(cltv_df, 'segment', col)