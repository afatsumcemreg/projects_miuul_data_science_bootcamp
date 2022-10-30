# import libraries
import pandas as pd
import math
import datetime as dt
import scipy.stats as st
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

# story of the dataset
# (50+ Saat) Python A-Z™: Veri Bilimi ve Machine Learning
# Puan: 4.8 (4.764925)
# Toplam Puan: 4611
# Puan Yüzdeleri: 75, 20, 4, 1, <1
# Yaklaşık Sayısal Karşılıkları: 3458, 922, 184, 46, 6

# reading the dataset
df = pd.read_csv('C:/Users/test/PycharmProjects/miuul_data_sicence_bootcamp/datasets/course_reviews.csv')
df.columns = [col.lower() for col in df.columns]
df.head()

# average

# rating distribution
df['rating'].value_counts()

# questions asked distribution
df['questions asked'].value_counts()

# get the rating mean in the questions asked breakdown
df.groupby('questions asked').agg({
    'questions asked': 'count',
    'rating': 'mean'})

# get the rating mean
df['rating'].mean()

# time-based weighted average

# changing type of the the variable 'timestamp' to 'datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.info()

# observing the comments date
current_day = pd.to_datetime('2021-02-10 0:0:0')
df['days'] = (current_day - df['timestamp']).dt.days

# get the comments in the last 30 days
df[df['days'] <= 30]

# get the rating counts in the last 30 days
df[df['days'] <= 30]['rating'].count()
df.loc[df['days'] <= 30, 'rating'].count()

# get the average of the ratings in the last 30 days (1. range)
df.loc[df['days'] <= 30, 'rating'].mean()

# get the average of the ratings between 30 and 90 days (2. range)
df.loc[(df['days'] > 30) & (df['days'] <= 90), 'rating'].mean()

# get the average of the ratings between 90 and 180 days (3. range)
df.loc[(df['days'] > 90) & (df['days'] <= 180), 'rating'].mean()

# get the average of the ratings after 180 days (4. range)
df.loc[df['days'] > 180, 'rating'].mean()

# considering the weights
# 1.range = 28%
# 2.range = 26%
# 3.range = 24%
# 4.range = 22%
# total of the percentages must be 100. 
df.loc[df['days'] <= 30, 'rating'].mean() * 0.28 + \
    df.loc[(df['days'] > 30) & (df['days'] <= 90), 'rating'].mean() * 0.26 + \
        df.loc[(df['days'] > 90) & (df['days'] <= 180), 'rating'].mean() * 0.24 + \
            df.loc[df['days'] > 180, 'rating'].mean() * 0.22

# functionalization of the above process
def time_based_weighted_average(dataframe, w1=0.28, w2=0.26, w3=0.24, w4=0.22):
    return dataframe.loc[dataframe['days'] <= 30, 'rating'].mean() * w1 + \
        dataframe.loc[(dataframe['days'] > 30) & (dataframe['days'] <= 90), 'rating'].mean() * w2 + \
            dataframe.loc[(dataframe['days'] > 90) & (dataframe['days'] <= 180), 'rating'].mean() * w3 + \
                dataframe.loc[dataframe['days'] > 180, 'rating'].mean() * w4

time_based_weighted_average(df)

# operating the function again by changing the weights
time_based_weighted_average(df, w1=0.30, w3=0.22)

# user-based weighted average

# aim: making a weighting related to the given rating according to the progress of the course
df.groupby('progress').agg({'rating': 'mean'}).sort_values('progress', ascending=False)

# considering the user weights
# for the progress > 75% = 28%
# 45% < the progress <= 75% = 26%
# 10% < the progress <= 45% = 24%
# for the progress <= 10% = 22%

df.loc[(df['progress'] <= 10), 'rating'].mean() * 0.22 + \
    df.loc[(df['progress'] > 10) & (df['progress'] <= 45), 'rating'].mean() * 0.24 + \
        df.loc[(df['progress'] > 45) & (df['progress'] <= 75), 'rating'].mean() * 0.26 + \
            df.loc[(df['progress'] > 75), 'rating'].mean() * 0.28

# functionalization of the above process
def user_based_weighted_average(dataframe, w1=0.22, w2=0.24, w3=0.26, w4=0.28):
    return dataframe.loc[(dataframe['progress'] <= 10), 'rating'].mean() * w1 + \
    dataframe.loc[(dataframe['progress'] > 10) & (dataframe['progress'] <= 45), 'rating'].mean() * w2 + \
        dataframe.loc[(dataframe['progress'] > 45) & (dataframe['progress'] <= 75), 'rating'].mean() * w3 + \
            dataframe.loc[(dataframe['progress'] > 75), 'rating'].mean() * w4

user_based_weighted_average(df)

# operating the function again by changing the weights
user_based_weighted_average(df, w1=0.20, w4=0.30)

# weighted rating

# combining the functions time_based_weighted_average and user_based_weighted_average
def weighted_rating(dataframe, time_w=0.50, user_w=0.50):
    return time_based_weighted_average(dataframe) * time_w + user_based_weighted_average(dataframe) * user_w

weighted_rating(df)

# operating the function again by changing the weights
weighted_rating(df, 0.4, 0.6)
weighted_rating(df, 0.6, 0.4)

# bayesian average rating
# if there is the distribution of the ratings, we can here apply the bayesian average rating function.