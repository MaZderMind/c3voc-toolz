#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import argparse
from time import time, sleep
import re
import json
import urllib2
import requests
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description='Watch a Folder for Video-Recordings, associate them with Talks from a Pentabarf-XML and upload the videos with metadata from the xml to Auphonic for further processing')
parser.add_argument('--schedule',
	required=True,
	help='url to a pentabarf schedule.xml')

parser.add_argument('--recordings',
	required=True,
	help='path of a folder with recording-files (mostly videos)')

parser.add_argument('--finished',
	help='path of a folder where uploaded files are moved to (defaults to a subfolder "finished" inside the recordings-folder)')

parser.add_argument('--auphonic-login',
	dest='auphonic',
	default=os.path.expandvars('$HOME/.auphonic-login'),
	help='path of a file containing "username:password" of your auphonic account')

parser.add_argument('--auphonic-preset',
	dest='preset',
	help='UUID of auphonic preset which should be used after uploading')

args = parser.parse_args()
if args.finished == None:
	args.finished = os.path.join(args.recordings, 'finished')


# try to read the auphonic login-data file
with open(args.auphonic) as fp:
	auphonic_login = fp.read().strip().split(':', 1)



# Download the Events-Schedule and parse all Events out of it. Yield a tupel for each Event
def fetch_events():
	print('downloading pentabarf schedule')

	# download the schedule
	response = urllib2.urlopen(args.schedule)

	# read xml-source
	xml = response.read()

	# parse into ElementTree
	schedule = ET.fromstring(xml)

	# destination list of events
	events = {}

	# iterate all days
	for day in schedule.iter('day'):
		# iterate all rooms
		for room in day.iter('room'):
			# iterate events on that day in this room
			for event in room.iter('event'):
				# aggregate names of the persons holding this talk
				personnames = []
				for person in event.find('persons').iter('person'):
					personnames.append(person.text)

				# yield a tupel with the event-id, event-title and person-names
				talkid = int(event.get('id'))
				events[talkid] = {
					'id': talkid,
					'title': event.find('title').text,
					'subtitle': event.find('subtitle').text,
					'abstract': event.find('abstract').text,
					'description': event.find('description').text,
					'personnames': ', '.join(personnames)
				}

	return events



def upload_file(filepath, event):
	print "creating Auphonic-Production for Talk-ID {0} '{1}'".format(event['id'], event['title'])

# curl -X POST -H "Content-Type: application/json" \
# 	https://auphonic.com/api/productions.json \
# 	-u `cat ~/.auphonic-login` \
# 	-d '{
# 		"preset": "DUgenUZvVDaHxP9qHgSHv8",
# 		"metadata": {
# 			"title": "Production Title",
# 			"artist": "The Artist",
# 			"subtitle": "Our subtitle",
# 			"summary": "Our very long summary."
# 		}
# 	}'
# 
# curl -X POST https://auphonic.com/api/production/KKw7AxpLrDBQKLVnQCBtCh/upload.json \
# 	-u username:password \
# 	-F "input_file=@minute.mp4"

	params = {
		"metadata": {
			"title": event['title'],
			"subtitle": event['subtitle'],
			"artist": event['personnames'],
			"summary": event['abstract']
		}
	}
	if args.preset:
		params['preset'] = args.preset

	r = requests.post(
		'https://auphonic.com/api/productions.json',
		auth=(auphonic_login[0], auphonic_login[1]),
		data=json.dumps(params),
		headers={'Content-Type': 'application/json'}
	)

	if r.status_code != 200:
		print "production creation failed with response: ", r, r.text
		return False

	production = r.json()['data']
	print "uploading {0} for Auphonic-Production {1}".format(filepath, production['uuid'])

	r = requests.post(
		'https://auphonic.com/api/production/{0}/upload.json'.format(production['uuid']),
		auth=(auphonic_login[0], auphonic_login[1]),
		files={'input_file': open(filepath, 'rb')}
	)

	if r.status_code != 200:
		print "upload failed with response: ", r, r.text
		return False

	return True


# initial download of the event-schedule
events = fetch_events()
eventsage = time()

pattern = re.compile("[0-9]+")

while True:
	# check age of event-schedule
	if time() - eventsage > 60*10:
		# re-download schedule when it's older then 10 minutes
		print('pentabarf schedule is >10 minutes old, re-downloading')

		# redownload
		events = fetch_events()
		eventsage = time()

	# iterate all files in the recordings-folder
	for filename in os.listdir(args.recordings):
		filepath = os.path.join(args.recordings, filename)

		# files, i said!
		if not os.path.isfile(filepath):
			continue

		# test if the filepath starts with a number and retrieve it
		match = pattern.match(filename)
		print('found file {0} in recordings-folder'.format(filename))
		if match:
			talkid = int(match.group(0))
			if talkid in events:
				event = events[talkid]
				if upload_file(filepath, event):
					print('done, moving to finished-folder')
					os.rename(filepath, os.path.join(args.finished, filename))
				else:
					print('upload FAILED! trying again, after the next Maus')


	# sleep half a minute
	print('nothing to do, sleeping half a minute')
	sleep(30)

print('all done, good night.')

