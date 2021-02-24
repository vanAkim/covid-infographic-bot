import tweepy

# Authenticate to Twitter
auth = tweepy.OAuthHandler("",                         # CONSUMER_KEY
    "")                       # CONSUMER_SECRET
auth.set_access_token("966718127076708352-",     # ACCESS_TOKEN
    "")                            # ACCESS_TOKEN_SECRET

api = tweepy.API(auth)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

timeline = api.home_timeline()
for tweet in timeline:
    print(f"{tweet.user.name} said {tweet.text}")

#api.update_status("Test tweet from Tweepy Python")



