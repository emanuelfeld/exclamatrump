#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time

import scraperwiki
import requests
import tweepy

from config import TWITTER_APP_KEY, TWITTER_APP_SECRET, TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_TOKEN_SECRET

def get_new_tweets(since_id, api):
    tweets = api.user_timeline(
        screen_name = 'realDonaldTrump', 
        count = 30, 
        since_id=since_id)

    if len(tweets) > 0:
        scraperwiki.sql.save(
            unique_keys=['id'], 
            data={'id': 1, 'index': tweets[0].id}, 
            table_name="progress")

    return tweets


def get_exclamations(tweet):
    if tweet.startswith('RT '):
        return ''
    if tweet.find(' RT @') > -1:
        tweet = tweet.split(' RT @')[0]
    tweet = re.sub(r'"@.*?("|$)', '', tweet)
    tweet = re.sub(r'[^!]+', '', tweet)
    return tweet


def update_profile(count):
    profile_text = str(count) + " and counting!"
    api.update_profile(
        "exclamatrump", 
        "https://twitter.com/exclamatrump", 
        "Washington, DC", 
        profile_text)


def make_status(tweet):
    status = exclamations + " https://twitter.com/realDonaldTrump/status/" + str(tweet.id)
    return status


def run(total_exclamations, since_id, api):
    tweets = get_new_tweets(since_id, api)
    print('{} new tweets'.format(len(tweets)))
    exclamation_tweets = 0
    for i in range(len(tweets))[::-1]:
        print(tweets[i].text)
        tweet_exclamations = get_exclamations(tweets[i].text)
        if len(tweet_exclamations) > 0:
            exclamation_tweets += 1
            total_exclamations += len(tweet_exclamations)
            status = tweet_exclamations + " https://twitter.com/realDonaldTrump/status/" + str(tweets[i].id)
            api.update_status(status)
            update_profile(total_exclamations, api)
            scraperwiki.sql.save(
                unique_keys=['id'], 
                data={'id': 1, 'count': total_exclamations}, 
                table_name="tally")
            time.sleep(2)
    print('{} new tweets with exclamations'.format(exclamation_tweets))


if __name__ == '__main__':
    twitter_auth = tweepy.OAuthHandler(TWITTER_APP_KEY, TWITTER_APP_SECRET)
    twitter_auth.set_access_token(TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_TOKEN_SECRET)
    api = tweepy.API(twitter_auth)
    try:
        total_exclamations = scraperwiki.sql.select("* from tally")[0]["count"]
        since_id = scraperwiki.sql.select("* from progress")[0]["index"]
    except:
        total_exclamations = 9176
        since_id = '917701841466593280'
    run(total_exclamations, since_id, api)
