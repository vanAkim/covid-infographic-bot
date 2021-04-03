import pandas as pd
import requests
import math
import numpy as np
import io
import tweepy
import os


#=======================================================================================================================
# From infographic_trend_squares.py

def trend_squares(rate_sqr, moving_sqr, empty_motif, filled_motif):
        ''' (number, number, str, str) -> str

        Return an aggregated column of special characters/emojis
        which is proportional in filled_motif by the rate_sqr input
        and empty_motif by the moving_sqr input.

        >>>trend_squares(0,4,"⬛","💟")
        "⬛\n⬛\n⬛\n⬛"
        >>>trend_squares(1,4,"⬛","💟")
        "⬛\n⬛\n⬛\n💟"
        >>>trend_squares(4,4,"⬛","💟")
        "💟\n💟\n💟\n💟"
        '''


        info_col = ""
        for i in range(0,rate_sqr):
                info_col = filled_motif + "\n" + info_col

        info_col = (empty_motif + "\n")*(moving_sqr-rate_sqr) + info_col

        return info_col


def join_trends(trends_sqr, empty_motif, filled_motif):
        ''' (list of str, str, str) -> str

        Return a string visually similar to a matrix of aggregated
        special characters/emojis columns from independant strings
        shaped like columns. Plus a full upper line of empty_motif
        and full lower line of filled_motif.

        >>>join_trends(['⬛\\n⬛\\n⬛\\n⬛\\n', '⬛\\n💟\\n💟\\n💟\\n'],"⬛","💟")
        '⬛⬛
        ⬛⬛
        ⬛💟
        ⬛💟
        ⬛💟
        💟💟'
        '''


        full_bloc = ''
        for i in np.arange(0, len(trends_sqr[0]), 2):
                full_bloc = full_bloc + '\n' + ''.join([fst_el[i] for fst_el in trends_sqr])

        full_bloc = full_bloc[1:len(full_bloc)] # remove 1st "\n"

        len_1line = len(trends_sqr)
        full_bloc = empty_motif*len_1line + "\n" + full_bloc + '\n' + filled_motif*len_1line

        return full_bloc


def info_bloc(data_byDays, moving_sqr, empty_motif, filled_motif):
        """ (Series of number, number, str, str) -> str

        Return a string visually similar to a matrix of aggregated
        special characters/emojis columns which each column is
        proportional in empty_motif by the input number values.

        >>>data_byDays = pd.Series([199,167,413])
        >>>info_bloc(data_byDays, 2,"⬛","💟")
        '⬛⬛⬛
        ⬛⬛💟 ← Max 413
        ⬛⬛💟
        💟💟💟 ← Min 167'
        """

        ## Round up all values with specific function
        data_byDays_scale = data_byDays.apply(lambda x: (x - min(data_byDays)) / (max(data_byDays) - min(data_byDays)))

        ## Create infographic bloc
        unit_bySquare = max(data_byDays_scale) / moving_sqr

        data_byDays_scale = data_byDays_scale.apply(dot3of5, args=(unit_bySquare,))

        relativ_rate = data_byDays_scale.apply(lambda x: int(x * moving_sqr))  # by number of squares: (0 3 2 etc)
        relativ_rate = relativ_rate.apply(trend_squares,
                                          args=(moving_sqr,
                                                empty_motif,
                                                filled_motif)).tolist()  # transformed into str columns: ['⬛\n⬛\n', '⬛\n💟\n', etc]

        info_blocs = join_trends(relativ_rate,
                                 empty_motif,
                                 filled_motif)  # transformed into full infographic bloc

        ## Adding min and max next to lines
        idx_endMax = len(data_byDays)*2 + 1                             # include one '\n'
        idx_end = (len(data_byDays) + 1)*(moving_sqr + 2)

        rounding = lambda x: round(x, 1 if x > 100 else 2)
        info_blocs = f"{info_blocs[0:idx_endMax]} ← Max {rounding(max(data_byDays))}{info_blocs[idx_endMax:idx_end]} " \
                     f"← Min {rounding(min(data_byDays))}"

        return info_blocs


#=======================================================================================================================
# From dot_round.py

def dot3of5(x,limit):
        """ number -> number

        Return a rounded number bounded to 0.6 of limit.

        >>>dot3of5(76,25)
        75
        >>>dot3of5(89,25)
        75
        >>>dot3of5(90,25)
        100
        >>>dot3of5(94,25)
        100
        """


        if x < (x//limit) * limit + 3*limit/5:
                return (x//limit) * limit

        else:
                return (x//limit) * limit + limit


#=======================================================================================================================
def tweet_strings(data_byDays, data_pddf, infograph_bloc, title, up_emoji, down_emoji, add_sticker=False, days_toCompute=10, moving_sqr=4):
        """
        :param data_byDays: Series of number of the explored data
        :param data_pddf: Data frame of all data
        :param infograph_bloc: String representing an infographic bloc
        :param title: String of the tweet 1st line
        :param up_emoji: String of a single character (emoji) of an increasing curve
        :param down_emoji: String of a single character (emoji) of a decreasing curve
        :param add_sticker: Boolean of whether adding a circle color and rounding the data or not. Used for % data.
        :param days_toCompute: Number of days to show in infographic (columns).
        :param moving_sqr: Numbers of lines to show in infrographic.
        :return: String of the full tweet, String of a positive or negative sign, Number of de difference value between previous and current day.
        """

        ## Adding some top lines to emphasize the infographic
        title_line = title

        trend_res = up_emoji if data_byDays.iloc[-1] > data_byDays.iloc[-2] else down_emoji

        ## Dual usage for % data: adding a color circle, rounding the number since isn't natural like others
        if add_sticker:
                orange = '🟠'
                red = '🔴'
                green = '🟢'

                color_res = red if data_byDays.iloc[-1] > 60 else (green if data_byDays.iloc[-1] < 30 else orange)
                color_res = f"{color_res} "

                today_data = f"{round(data_byDays.iloc[-1], 2)}%"

                lgd_data = f"{round((max(data_byDays) - min(data_byDays)) / moving_sqr, 2)}%"
        else:
                color_res = ""

                today_data = f"{data_byDays.iloc[-1]}"

                lgd_data = f"{math.floor((max(data_byDays) - min(data_byDays)) / moving_sqr)}"


        today_line = f"{data_pddf.loc[data_pddf.shape[0] - 1, 'date']}: {color_res}{today_data} {trend_res}"

        lstDays_line = f"👇Données {days_toCompute} derniers jours👇"

        lgdSqr_line = f"Légende: {filled_pattern}≈ {lgd_data}"


        ## Wrap-up
        infograph_bloc = title_line + '\n\n' + \
                         today_line + '\n\n' + \
                         lstDays_line + '\n' + \
                         infograph_bloc + '\n\n' + \
                         lgdSqr_line


        # Used in retweets to get the precise difference value from n-1 to current day
        sign_res = "+" if trend_res == up_emoji else "-"
        diff_today = abs(data_byDays.iloc[-1] - data_byDays.iloc[-2])

        return [infograph_bloc, sign_res, diff_today]


#=======================================================================================================================
# From write-pattern-twit.py


#-----------------------------------------------------------------------------------------------------------------------
## Download dataframe

url = "https://www.data.gouv.fr/fr/datasets/r/f335f9ea-86e3-4ffa-9684-93c009d5e617" # URL stable
# myfile = requests.get(url)
# open('data/table-indicateurs-open-data-france.csv', 'wb').write(myfile.content)


## Load overall dataframe
myfile = requests.get(url).content
df = pd.read_csv(io.StringIO(myfile.decode('utf-8')))


## Overall parameters to construct the infographic
days_toCompute = 10
moving_squares = 4  # seems to be the more elegant infographic pattern
down_pattern = "📉"
up_pattern = "📈"


#-----------------------------------------------------------------------------------------------------------------------
# Tension hospitalière sur la capacité en réanimation

## Parameters to construct the infographic
empty_pattern = "⬛"
filled_pattern = "💟"


## Get only the required values from data
rate_days = df.loc[df.shape[0] - days_toCompute: df.shape[0] + 1,
             "TO"]

## Turn proportions into %
rate_days = rate_days.apply(lambda x: x*100)


## Create infographic bloc
infographic_hosOccRate = info_bloc(rate_days,
                               moving_squares,
                               empty_pattern,
                               filled_pattern)


## Create main tweet with top lines and infograph
title_line = "Tension hospitalière en réanimation"

infographic_hosOccRate, sign_res, diff_value = tweet_strings(rate_days, df, infographic_hosOccRate,
                                                          title_line,
                                                          up_pattern, down_pattern,
                                                          True, days_toCompute, moving_squares)

## Following up tweet with sources

rt_expl_hosOccRate = "Proportion de patients atteints de COVID-19 actuellement en réanimation, en soins intensifs, " \
                     "ou en unité de surveillance continue rapportée au total des lits en capacité initiale, c’est-à-dire " \
                     "avant d’augmenter les capacités de lits de réanimation dans un hôpital"

rt_exactNmb = f"Différence exacte depuis 24h: {sign_res}{round(diff_value,2)}%"

rt_sources = f"Sources et données: @SantePubliqueFr @datagouvfr" \
             f"\nhttps://www.data.gouv.fr/fr/datasets/synthese-des-indicateurs-de-suivi-de-lepidemie-covid-19/#_" \
             f"\nhttps://www.data.gouv.fr/fr/datasets/indicateurs-de-suivi-de-lepidemie-de-covid-19/#_"

rt_hosOccRate = rt_exactNmb + '\n' + rt_sources


#-----------------------------------------------------------------------------------------------------------------------
# Nombre de patients actuellement hospitalisés pour COVID-19


## Parameters to construct the infographic
empty_pattern = "⬛"
filled_pattern = "🥼"


## Get only the required values from data
rate_days = df.loc[df.shape[0] - days_toCompute: df.shape[0] + 1,
             "hosp"].astype(int)


## Create infographic bloc
infographic_hosPpl = info_bloc(rate_days,
                               moving_squares,
                               empty_pattern,
                               filled_pattern)


## Create main tweet with top lines and infograph
title_line = "Patients hospitalisés pour COVID-19"


infographic_hosPpl, sign_res, diff_value = tweet_strings(rate_days, df, infographic_hosPpl,
                                                      title_line,
                                                      up_pattern, down_pattern,
                                                      False, days_toCompute, moving_squares)


## Following up tweet with sources

rt_expl = ""

rt_exactNmb = f"Différence exacte depuis 24h: {sign_res}{diff_value}"

rt_sources = f"Sources et données: @SantePubliqueFr @datagouvfr" \
             f"\nhttps://www.data.gouv.fr/fr/datasets/synthese-des-indicateurs-de-suivi-de-lepidemie-covid-19/#_"

rt_hosPpl = rt_exactNmb + '\n' + rt_sources


#-----------------------------------------------------------------------------------------------------------------------
# Nouveaux patients décédés à l’hôpital au cours des dernières 24h pour cause de COVID-19


## Parameters to construct the infographic
empty_pattern = "⬛"
filled_pattern = "⚰"


## Get only the required values from data
rate_days = df.loc[df.shape[0] - days_toCompute: df.shape[0] + 1,
             "incid_dchosp"].astype(int)


## Create infographic bloc
infographic_dcHos = info_bloc(rate_days,
                              moving_squares,
                              empty_pattern,
                              filled_pattern)


## Create main tweet with top lines and infograph
title_line = "Décès à l’hôpital pour COVID-19 (hors EHPAD/ESMS)"

infographic_dcHos, sign_res, diff_value = tweet_strings(rate_days, df, infographic_dcHos,
                                                        title_line,
                                                        up_pattern, down_pattern,
                                                        False, days_toCompute, moving_squares)


## Following up tweet with sources

rt_expl = ""

rt_exactNmb = f"Différence exacte depuis 24h: {sign_res}{diff_value}"

rt_sources = f"Sources et données: @SantePubliqueFr @datagouvfr" \
             f"\nhttps://www.data.gouv.fr/fr/datasets/synthese-des-indicateurs-de-suivi-de-lepidemie-covid-19/#_"

rt_dcHos = rt_exactNmb + '\n' + rt_sources


# print(infographic_hosOccRate)
# print(infographic_hosPpl)
# print(infographic_dcHos)

# twit_txtfile = infographic_hosOccRate + '\n' + rt_hosOccRate + '\n' +\
#                infographic_hosPpl + '\n' + rt_hosPpl + '\n' + \
#                infographic_dcHos + '\n' + rt_dcHos


# with io.open('tweets.txt', 'w', encoding='utf8') as f:
#     f.write(twit_txtfile)


#=======================================================================================================================


# Authenticate to Twitter
user_api = os.getenv("user_api")
user_key = os.getenv("user_key")
content_api = os.getenv("content_api")
content_key = os.getenv("content_key")


auth = tweepy.OAuthHandler(user_api, user_key)        # CONSUMER_KEY, CONSUMER_SECRET
auth.set_access_token(content_api, content_key)       # ACCESS_TOKEN, ACCESS_TOKEN_SECRET

api = tweepy.API(auth)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

# Write main tweets

## Hosp rate infographic tweet
api.update_status(infographic_hosOccRate)

## Retweet with explanation about the metric
tweets = api.home_timeline(count=1)
tweet = tweets[0]
api.update_status(rt_expl_hosOccRate, in_reply_to_status_id = tweet.id)

## Retweet with sources
tweets = api.home_timeline(count=1)
tweet = tweets[0]
api.update_status(rt_hosOccRate, in_reply_to_status_id = tweet.id)



## Hosp ppl infographic tweet
api.update_status(infographic_hosPpl)

## Retweet with sources
tweets = api.home_timeline(count=1)
tweet = tweets[0]
api.update_status(rt_hosPpl, in_reply_to_status_id = tweet.id)



## Death infographic tweet
api.update_status(infographic_dcHos)

## Retweet with sources
tweets = api.home_timeline(count=1)
tweet = tweets[0]
api.update_status(rt_dcHos, in_reply_to_status_id = tweet.id)
