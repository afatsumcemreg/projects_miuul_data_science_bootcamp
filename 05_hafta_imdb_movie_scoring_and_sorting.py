##############################################
# importing the libraries
##############################################
from itertools import count
from operator import ne
from numpy import average
import pandas as pd
import math 
import scipy.stats as st
from sklearn.preprocessing import MinMaxScaler
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.max_rows', 20)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
pd.set_option('display.expand_frame_repr', False)

# reading the dataset
df = pd.read_csv('C:/Users/test/PycharmProjects/miuul_data_sicence_bootcamp/datasets/movies_metadata.csv', low_memory=False)
df.head()
df.shape

##############################################
# selecting the related variables
##############################################
df = df[['title', 'vote_average', 'vote_count']]
df.head()

# purpose: updating the list top250 , which is referenced by many people

# sorting according the tha variable vote_average
df.sort_values('vote_average', ascending=False).head(20)

# filtering the variable 'vote_count' accorting to a certain vote count
df['vote_count'].describe([0.1, 0.25, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99]).T

# the basic motivation is to recommend a certain number (250) of movies

# filtering according to vote_count > 400
df[df['vote_count'] > 400].sort_values('vote_average', ascending=False)

# standardization the values of the variable vote_count
df['vote_count_score'] = MinMaxScaler(feature_range=(1, 10)).fit_transform(df[['vote_count']])
# df['vote_count_score'] = MinMaxScaler(feature_range=(1, 10)).fit(df[['vote_count']]).transform(df[['vote_count']]) # other method

# multiply the vote count and vote average and create a new variable named 'average_count_score'
df['average_count_score'] = df['vote_count_score'] * df['vote_average']
df.sort_values('average_count_score', ascending=False).head(20)

##############################################
# IMDB weighted rating
##############################################

# weighted rating = (v/(v+M) * r) + (M/(v+M) * c)
# r = vote average
# v = vote count
# M = minimum votes rquired to be listed in the top250
# c = mean vote acros the whole report (current value = 7.0)
# until 2015, this formula was used to calculate the imdb ratings

# defing a function for the above formula
def weighted_rating(r, v, M, c):
    return (v/(v+M) * r) + (M/(v+M) * c)

M = 2500
c = df['vote_average'].mean()
weighted_rating(7.4, 11444, M, c)   # for the film 'deadpool'
weighted_rating(8.1, 14075.00, M, c)   # for the film 'inception'
weighted_rating(8.5, 8358.00, M, c)   # for the film 'The Shawshank Redemption'

# applying the defined function to the whole data
df['weighted_rating'] = weighted_rating(df['vote_average'], df['vote_count'], M, c)
df.sort_values('weighted_rating', ascending=False).head(20)

##############################################
# bayesian average rating score
##############################################

# defining a Bayesian Average Rating function
def bayesian_average_rating(n, confidence=0.95):    # n = number of each star given
    if sum(n) == 0:
        return 0
    K = len(n)
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    N = sum(n)
    first_part = 0.0
    second_part = 0.0
    for k, n_k in enumerate(n):
        first_part += (k + 1) * (n[k] + 1) / (N + K)
        second_part += (k + 1) * (k + 1) * (n[k] + 1) / (N + K)
    score = first_part - z * math.sqrt((second_part - first_part * first_part) / (N + K + 1))
    return score

# calculating the IMDB scor the the film 'The Shawshank Redemption'
bayesian_average_rating([34733, 4355, 4704, 6561, 13515, 26183, 87368, 273082, 600260, 1295351]) # the numbers are the distribution of stars given

# calculating the IMDB scor the the film 'The Godfather'
bayesian_average_rating([37128, 5879, 6268, 8419, 16603, 30016, 78538, 199430, 402518, 837905])

# application of bayesian_average_rating function to the new dataset to calcualate the IMDB scores of the movies
new_df = pd.read_csv('C:/Users/test/PycharmProjects/miuul_data_sicence_bootcamp/datasets/imdb_ratings.csv')
new_df = new_df.iloc[0:, 1:]
new_df.head()
new_df['bar_score'] = new_df.apply(lambda x: bayesian_average_rating(x[['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']]), axis=1)
new_df.sort_values('bar_score', ascending=False).head(20)