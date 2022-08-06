#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  3 23:02:30 2022

@author: zevburton
"""

# package import  

import tweepy
import time
import pandas as pd
import networkx as nx

#%% Remove Before Commit
# using my twitter api key, will remove before commit
 
api_key = "..."
api_secrets = "..."
access_token = "..."
access_secret = "..."

bearer = "..."

#%% API calls
# connecting tweepy to twitter api
client = tweepy.Client(bearer_token=bearer)


# authorization of consumer key and consumer secret
auth = tweepy.OAuthHandler(api_key, api_secrets)
  
# set access to user's access key and access secret 
auth.set_access_token(access_token, access_secret)
  
# calling the api 
api = tweepy.API(auth, wait_on_rate_limit=True)

## getting the usernames of the 116th congress

# Reading CSVs and brief data formatting adjustments
house_twitter = pd.read_csv("congress116-house-accounts.csv")
house_ids = house_twitter['Uid'].tolist()
house_users = house_twitter['Token'].tolist()
senate_twitter = pd.read_csv("congress116-senate-accounts.csv")
senate_ids = senate_twitter['Uid'].tolist()
senate_users = senate_twitter['Token'].tolist()

# combining house and senate twitter users and ids
all_users = house_users + senate_users
all_ids = house_ids + senate_ids

# Create Network
G = nx.DiGraph()

## cycling through politicians

# counter
i = 0
while i/944 <= 1:
        for id in all_ids:
            index = all_ids.index(id) # getting twitter id
            username = all_users[index + 396] # getting twitter username

            try:
                paginator = tweepy.Paginator( # going through the people they're following
                    client.get_users_following,
                    id,
                    max_results = 150,
                    limit = 15)
    
                for tweet in paginator.flatten(): # flatten list
                    current = str(tweet)
                    if current in all_users: # see if their following other politicians
                        print("Going from ", username, " to ", current)
                        G.add_edge(username, current) # adding edges (and nodes implicitly) to graph
                    time.sleep(.1) # sleep
                i = i + 1 # adjust counter
                print(i / 9.44) # print percentage done
            except tweepy.TooManyRequests: # if twitter overload, sleep for 15 minutes, 
                                           # the amount of time it takes for twitter to refresh api calls
                print("Pause", username) # replace this before commit
                time.sleep(60 * 15) # 15 min sleep
                continue

# write

nx.write_gml(G, "following_graph")
