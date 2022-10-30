##############################################
# Case Study
##############################################

##############################################
# preparing a datafram from an e-trade company
##############################################

up = [15, 70, 14, 4, 2, 5, 8, 37, 21, 52, 28, 147, 61, 30, 23, 40, 37, 61, 54, 18, 12, 68]
down = [0, 2, 2, 2, 15, 2, 6, 5, 23, 8, 12, 2, 1, 1, 5, 1, 2, 6, 2, 0, 2, 2]
df = pd.DataFrame({"up": up, "down": down})

##############################################
# adding the 'scores_pos_ned_diff' variable
##############################################

def scores_pos_ned_diff(up, down):
    return up - down

df['scores_pos_ned_diff'] = df.apply(lambda x: scores_pos_ned_diff(x['up'], x['down']), axis=1)

##############################################
# adding the 'score_average_rating' variable
##############################################

def score_average_rating(up, down):
    if up + down == 0: return 0
    return up / (up + down)

df['score_average_rating'] = df.apply(lambda x: score_average_rating(x['up'], x['down']), axis=1)

##############################################
# adding the 'wilson_lower_bound' variable
##############################################

def wilson_lower_bound(up, down, confidence=0.95):
    n = up + down
    if n == 0: return 0
    z = st.norm.ppf(1 - (1 - confidence) / 2)
    phat = 1.0 * up / n
    return (phat + z * z / (2 * n) - z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)

df['wilson_lower_bound'] = df.apply(lambda x: wilson_lower_bound(x['up'], x['down']), axis=1)

# sorting the dataframe by 'wlb' scores
df.sort_values('wilson_lower_bound', ascending=False)