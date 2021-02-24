import tweepy
import os

# Authenticate to Twitter
auth = tweepy.OAuthHandler(os.getenv("user_api"),                         # CONSUMER_KEY
    os.getenv("user_key"))                       # CONSUMER_SECRET
auth.set_access_token(os.getenv("content_api"),     # ACCESS_TOKEN
    os.getenv("content_key"))                            # ACCESS_TOKEN_SECRET

api = tweepy.API(auth)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

timeline = api.home_timeline()
for tweet in timeline:
    print(f"{tweet.user.name} said {tweet.text}")

api.update_status("Test tweet from Tweepy Python")



