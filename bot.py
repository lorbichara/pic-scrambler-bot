import tweepy
import requests
import random
from io import BytesIO
from PIL import Image
from PIL import ImageFile

from secrets import *

#create OAuthHandler instance for authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
#Construct API instance
api = tweepy.API(auth) #API object

def tweet_image(url, username, status_id):
	filename = 'temp.png'
	request = requests.get(url, stream=True)
	if request.status_code == 200:
		i = Image.open(BytesIO(request.content))
		i.save(filename)
		scramble(filename)
		api.update_with_media('scramble.png', status='@{0}'.format(username), in_reply_to_status_id=status_id)
	else:
		print("unable to download image")
	
def scramble(filename):
	BLOCKLEN = 64
	img = Image.open(filename)
	width, height = img.size

	xblock = width // BLOCKLEN
	yblock = height // BLOCKLEN
	blockmap = [(xb * BLOCKLEN, yb * BLOCKLEN, (xb + 1) * BLOCKLEN, (yb + 1) * BLOCKLEN)
				for xb in range(xblock) for yb in range(yblock)]

	shuffle = list(blockmap)

	random.shuffle(shuffle)

	result = Image.new(img.mode, (width, height))
	for box, sbox in zip(blockmap, shuffle):
		crop = img.crop(sbox)
		result.paste(crop, box)
	result.save('scramble.png')

class BotStreamer(tweepy.StreamListener):
    # Called when a new status arrives which is passed down from the on_data method of the StreamListener
    def on_status(self, status):
        username = status.user.screen_name
        status_id = status.id

        # entities provide structured data from Tweets including resolved URLs, media, hashtags and mentions without having to parse the text to extract that information
        if 'media' in status.entities:
            for image in status.entities['media']:
                tweet_image(image['media_url'], username, status_id)

myStreamListener = BotStreamer()
# Construct the Stream instance
stream = tweepy.Stream(auth, myStreamListener)
stream.filter(track=['@picscrambler'])