import os
import random

import atproto_client.exceptions
from atproto import Client, models
from dotenv import load_dotenv

#load sys env vars
load_dotenv()


#create help functs
#add id to posts we've replied to
def add_to_posts_replied_to(postId):
    f = open("postsReplyedTo.txt", "a")
    f.write("\n" + postId)
    f.close()

#have we already replied to this post?
def is_in_posts_replied_to(postId):
    f = open("postsReplyedTo.txt", "r")
    idDone = postId in f.read()
    f.close()
    return idDone

#num of spaces in str
def num_of_spaces(input: str) -> int:
    count = 0
    for i in input:
        if i == " ":
            count += 1
    return count

#detects defects in posts
def defect_detector(input: str) -> str:
    return "No Defects. No Defects"


#length of input spelled out
def numbers_to_words(inputLen: int) -> str:
    output: str = ""
    inputAsStr: str = str(inputLen)
    if inputLen < 10:
        inputAsStr = "0" + inputAsStr
    if inputLen < 100:
        inputAsStr = "0" + inputAsStr
    for i in range(0, len(inputAsStr)):
        currentChar = inputAsStr[i]
        if(currentChar == '0'):
            output += "Zero "
        elif(currentChar == '1'):
            output += "One "
        elif(currentChar == '2'):
            output += "Two "
        elif(currentChar == '3'):
            output += "Three "
        elif(currentChar == '4'):
            output += "Four "
        elif(currentChar == '5'):
            output += "Five "
        elif(currentChar == '6'):
            output += "Six "
        elif(currentChar == '7'):
            output += "Seven "
        elif(currentChar == '8'):
            output += "Eight "
        else:
            output += "Nine "
    return output

#figures out how many times we've replied
def get_times_replied():
    f = open("TimesReplyed.txt")
    text = f.read()
    f.close()
    return len(text)

#adds one to times replied
def update_times_replied():
    f = open("TimesReplyed.txt","a")
    f.write("a")
    f.close()

#creates reply
def replyTextCreator(postText: str) -> str:
    output = ("Bluesky Post Defect Detector. \n"
              "Post " + numbers_to_words(get_times_replied()) + ".\n"
              + defect_detector(postText) + ".\n"
              "Number of letters " + numbers_to_words(len(postText)) + ".\n"
              "Number of spaces " + numbers_to_words(num_of_spaces(postText)) +".\n"
              "End of transmission.")
    return output

def get_posts(feedList):
    try:
        #get the URI of the random feed
        feedUri = feedList[random.randint(0, len(feedList) -1)].uri
        #recursively try to get posts from that URI
        try:
            data = client.app.bsky.feed.get_feed({
                'feed': feedUri,
                'limit': 30,
            }, headers={'Accept-Language': ""})
            return data
        except atproto_client.exceptions.NetworkError:
            return get_posts(feedUri)
    except AttributeError:
        print("No URI")

#grabs a random post
def grab_random_post(data):
    return data[random.randint(0, len(data) - 1)]

#Setup Client
client: Client = Client()
client.login(str(os.getenv('BSKYUSERNAME')),str(os.getenv('PASSWORD')))

def createPost(index):
    #Get random feed
    feedList = client.app.bsky.unspecced.get_popular_feed_generators().feeds


    data = get_posts(feedList).feed
    # If feed has posts
    if len(data) > 0:
        # Get a random post
        randPost = grab_random_post(data).post
        while is_in_posts_replied_to(randPost.uri):
            randPost = grab_random_post(data).post
        # add post id to list of posts that we've replied to
        add_to_posts_replied_to(randPost.uri)
        # Get post text
        randPostText = randPost.record.text
        # Create a reference to the post
        parent = models.create_strong_ref(randPost)
        # Reply using that reference
        client.send_post(
            text=replyTextCreator(randPostText),
            reply_to=models.AppBskyFeedPost.ReplyRef(parent=parent, root=parent)
        )
        # update the times replied
        update_times_replied()
    if (index > 0):
        createPost(index - 1)


createPost(5)
