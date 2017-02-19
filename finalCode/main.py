import json
import cv2
import sys
import csv
import pyaudio  
import wave
import requests
import twitter
import config
import time
import serial
import pygame
from random import randint 
from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3, TextToSpeechV1
from math import *
 
def start(prof):
	with open('data', 'rb') as f:
	    reader = csv.reader(f)
	    your_list = list(reader)

	#print len(your_list)
	#print len(your_list[1])
	data_list = []

	for i in range(0, len(your_list)):
		temp = []
		for j in range(1,53):
			temp.append(float(your_list[i][j].strip()))
		data_list.append([your_list[i][0], temp, your_list[i][-1]])

	#print len(data_list)

	cosine_list = []

	def convert_status_to_pi_content_item(s):
	    # My code here
	    return { 
		'userid': str(s.user.id), 
		'id': str(s.id), 
		'sourceid': 'python-twitter', 
		'contenttype': 'text/plain', 
		'language': s.lang, 
		'content': s.text, 
		'created': 1000 * s.GetCreatedAtInSeconds(),
		'reply': (s.in_reply_to_status_id == None),
		'forward': False
	    }
	twitter_api = twitter.Api(consumer_key=config.twitter_consumer_key,
		          consumer_secret=config.twitter_consumer_secret,
		          access_token_key=config.twitter_access_token,
		          access_token_secret=config.twitter_access_secret,
		          debugHTTP=True)    
	users = 3
	statuses = [] 
	for i in range(1,users): 
		handle = prof
		
		
		
		
		
		statuses += twitter_api.GetUserTimeline(screen_name=handle,
		          count=200,
		          include_rts=False)
	#print "Statuses are..."
	#print statuses
	

	pi_content_items_array = map(convert_status_to_pi_content_item, statuses)
	pi_content_items = { 'contentItems' : pi_content_items_array }

	r = requests.post(config.pi_url + '/v2/profile', 
				auth=(config.pi_username, config.pi_password),
				headers = {
		        'content-type': 'application/json',
		        'accept': 'application/json'
		    },
				data=json.dumps(pi_content_items)
			)
	#print("Profile Request sent. Status code: %d, content-type: %s" % (r.status_code, r.headers['content-type']))
	j = json.loads(r.content)
	insights  = []
	big_five = []
	details = []
	needs = []
	values = []

	#print j
	#print "Breaking here....\n"

	#for i in j['tree']['children'][0]['children'][0]['children'][0]['children'][0]:
	#	print i

	for i in range (0,5):
		big_five.append(( j['tree']['children'][0]['children'][0]['children'][i]['name'],
	j['tree']['children'][0]['children'][0]['children'][i]['percentage']))
		insights.append(( j['tree']['children'][0]['children'][0]['children'][i]['name'],
	j['tree']['children'][0]['children'][0]['children'][i]['percentage']))

		for k in range(0,6):
			details.append((j['tree']['children'][0]['children'][0]['children'][i]['children'][k]['name'],
	j['tree']['children'][0]['children'][0]['children'][i]['children'][k]['percentage']))
			insights.append((j['tree']['children'][0]['children'][0]['children'][i]['children'][k]['name'],
	j['tree']['children'][0]['children'][0]['children'][i]['children'][k]['percentage']))


	print "PRINTING>>>>>"
	#print big_five
	
	#emotional_range = big_five[4][1]
	#agree = big_five[3][1]
	#openness = big_five[0][1]


	
	 
	for p in range(0,12):
		needs.append( (j['tree']['children'][1]['children'][0]['children'][p]['name'],j['tree']['children'][1]['children'][0]['children'][p]['percentage']))
		insights.append( (j['tree']['children'][1]['children'][0]['children'][p]['name'],j['tree']['children'][1]['children'][0]['children'][p]['percentage']))

		
	#print "BREAK \n"
	#print needs

	for p in range(0,5):
		values.append( (j['tree']['children'][2]['children'][0]['children'][p]['name'],j['tree']['children'][2]['children'][0]['children'][p]['percentage']))
		insights.append( (j['tree']['children'][2]['children'][0]['children'][p]['name'],j['tree']['children'][2]['children'][0]['children'][p]['percentage']))

	#print "BREAK!!"
	#print values
	#for n in j['tree']['children'][2]['children']:
	 #   print n   #gives needs
	#print insights
	insights_num = []
	for i in range(0,len(insights)):
		insights_num.append((insights[i][0], i))
	
	#print insights_num
		
	environment_friendly = insights[51][1]
	self_enhancement = insights[50][1]
	adventure = insights[1][1]
	outgoing = insights[19][1]
	emotional = insights[3][1]
	romantic = insights[42][1]
	artistic_interests = insights[2][1]
	intellect = insights[5][1]
	openness = insights[0][1]
	
	personality_list = [51,50,1,19,3,42,2,5,0]
	personality_type = []
	
	for i in personality_list:
		personality_type.append((insights[i][0],insights[i][1]))
	
	print personality_type
	
	
	personality_type.sort(key=lambda x: x[1])
	final =  personality_type[::-1]
	
	my_string = "Your personality trait evident is " + str(final[0][0]) + " with percentile " +  str(final[0][1])
	
	print my_string
	return str(final[0][0])
 
def textToSpeechWelcome(msg):
	text_to_speech = TextToSpeechV1(
			username='865d2184-6e59-448e-aa5c-dfae8a72f406',
			password='g0pNTs6LeZki',
			x_watson_learning_opt_out=True)  # Optional flag

	with open(join(dirname(__file__), '../resources/output.wav'),
			  'wb') as audio_file:
		audio_file.write(
			text_to_speech.synthesize(msg, accept='audio/wav',
			                          voice="en-US_AllisonVoice"))	
	
	#define stream chunk   
	chunk = 1024  

	#open a wav format music  
	f = wave.open("../resources/output.wav","rb")  
	#instantiate PyAudio  
	p = pyaudio.PyAudio()  
	#open stream  
	stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
		            channels = f.getnchannels(),  
		            rate = f.getframerate(),  
		            output = True)  
	#read data  
	data = f.readframes(chunk)  

	#play stream  
	while data:  
		stream.write(data)  
		data = f.readframes(chunk)  

	#stop stream  
	stream.stop_stream()  
	stream.close()  

	#close PyAudio  
	p.terminate()
	
def playVideo(vid):
	pygame.init()
	pygame.mouse.set_visible(False)
	pygame.mixer.quit()
	screen = pygame.display.set_mode((320, 240))
	video = pygame.movie.Movie(vid)
	screen = pygame.display.set_mode(video.get_size())
	video.play()
	time.sleep(3)
	while video.get_busy():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				break

def detectAges(filea):
	visual_recognition = VisualRecognitionV3('2016-05-20', api_key='31b4a7b4a13baf31bb492ac1e1e42b1ab5dcc62e')
	
	with open(join(dirname(__file__), 'test_image.png'), 'rb') as image_file:        
		output_string=json.dumps(visual_recognition.detect_faces(images_file=image_file),indent=2)

	output_json=json.loads(output_string)
	faces=output_json["images"][0]["faces"]
	male_c= 0
	female_c = 0
	for i in range(0,len(faces)):
						print "person ",i
						print "				gender:",faces[i]["gender"]["gender"]
						if(faces[i]["gender"]["gender"] == "MALE" and faces[i]["gender"]["score"] > 0.5 ):
							male_c += 1
						if(faces[i]["gender"]["gender"] == "FEMALE" and faces[i]["gender"]["score"] > 0.5):
							female_c += 1
						print "				gender score:",faces[i]["gender"]["score"]
						if len(faces[i]["age"])>2:
											print "    max age:",faces[i]["age"]["max"]
											print "    min age:",faces[i]["age"]["min"]
											print "    age score:",faces[i]["age"]["score"]
						else:
										print "has more than 2"
	if(male_c > female_c):
		return 1
	else:
		return 0

if __name__ == "__main__":
	name=[]
	profile=[]
	floor=[]
	gender=[]
	ids={" 3E B2 92 ":("Abhijay","abhijayarora","60th","M")," 3E FB F9 ":("aravind","inaps27","70th", "M")," 3E F5 D6 ":("Kaushik","imkaushikt","80th","M")}
	arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=.1)
	wait=0
	while wait<7:
		data = arduino.readline()[:-2] 
		if data:
			#print "-",data,"-"
			if data in ids.keys():
				name.append(ids[data][0])
				profile.append(ids[data][1])
				floor.append(ids[data][2])
				gender.append(ids[data][3])
				welcome_msg ='Welcome ' + name[-1] + ', you are going to '+ floor[-1] + ' Floor!!'
				print welcome_msg				
				textToSpeechWelcome(welcome_msg)
				#time.sleep(3)				
			else:
				print "Unknown Card"
		else:
			time.sleep(1)
		wait=wait+1
	if len(name)<1:
		textToSpeechWelcome("No RFID Tag detected")
		#time.sleep(2)	

		# Camera 0 is the integrated web cam on my netbook
		camera_port = 0

		#Number of frames to throw away while the camera adjusts to light levels
		ramp_frames = 30
		 
		# Now we can initialize the camera capture object with the cv2.VideoCapture class.
		# All it needs is the index to a camera port.
		camera = cv2.VideoCapture(camera_port)
		 
		# Captures a single image from the camera and returns it in PIL format
		def get_image():
		 # read is the easiest way to get a full image out of a VideoCapture object.
		 retval, im = camera.read()
		 return im
		 
		# Ramp the camera - these frames will be discarded and are only used to allow v4l2
		# to adjust light levels, if necessary
		for i in xrange(ramp_frames):
		 temp = get_image()
		textToSpeechWelcome("Taking your picture")
		#time.sleep(2)
		# Take the actual image we want to keep
		camera_capture = get_image()
		filea = "test_image.png"
		# A nice feature of the imwrite method is that it will automatically choose the
		# correct format based on the file extension you provide. Convenient!
		cv2.imwrite(filea, camera_capture)
		img = cv2.imread(filea)
		cv2.imshow('image',img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		# You'll want to release the camera, otherwise you won't be able to create a new
		# capture object until your script exits
		del(camera)
		if(detectAges(filea) == 1):
			textToSpeechWelcome("Men outnumbered women in the elevator.")
			#time.sleep(3)							
			playVideo("boys.mpg")
		else:
			textToSpeechWelcome("Women outnumbered Men in the elevator")
			#time.sleep(3)
			playVideo("jwellery.mpg")
	else:
		persIns = start(profile[randint(0,len(name)-1)])
		persInsStr = 'Your personality seems to be ' + persIns +'. This is a personalized advertisement for you.'
		textToSpeechWelcome(persInsStr)
		time.sleep(4)
		mov_name = ""
		if(persIns == "Adventurousness"):
			mov_name = "adventurousness.mpg"
		elif(persIns == "Outgoing"):
			mov_name = "club.mpg"
		elif(persIns == "Openness" and gend == "M"):
			mov_name = "openness.mpg"
		elif(persIns == "Openness" and gend == "F"):
			mov_name = "openness.mpg"
		elif(persIns == "Self-transcendence"):
			mov_name = "transcendence.mpg"
		elif(persIns == "Self-enhancment"):
			mov_name = "enhancment.mpg"
		elif(persIns == "Emotionality"):
			mov_name = "emotionality.mpg"
		elif(persIns == "Love"):
			mov_name = "romantic.mpg"
		elif(persIns == "Artistic Interest"):
			mov_name = "artistic.mpg"
		elif(persIns == "Intellect"):
			mov_name = "intellect.mpg"
		playVideo(mov_name)	
		
