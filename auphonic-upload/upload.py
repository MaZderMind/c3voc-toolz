#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import sys
import errno
import argparse
from time import time, sleep
import re
import requests
from poster.encode import multipart_encode
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description='Watch a Folder for Video-Recordings, associate them with Talks from a Pentabarf-XML and upload the videos with metadata from the xml to Auphonic for further processing')
parser.add_argument('--schedule',
	required=True,
	help='url to a pentabarf schedule.xml')

parser.add_argument('--recordings',
	required=True,
	help='path of a folder with recording-files (mostly videos)')

parser.add_argument('--finished',
	help='path of a folder where uploaded files are moved to (defaults to a subfolder "finished-upload" inside the recordings-folder)')

parser.add_argument('--extension',
	help='only work on files with the given extension')

parser.add_argument('--auphonic-login',
	dest='auphonic',
	default=os.path.expandvars('$HOME/.auphonic-login'),
	help='path of a file containing "username:password" of your auphonic account')

parser.add_argument('--auphonic-preset',
	dest='preset',
	help='UUID of auphonic preset which should be used after uploading')

args = parser.parse_args()

# if no finished-folder was specified, construct one
if args.finished == None:
	args.finished = os.path.join(args.recordings, 'finished-upload')

# ensure it exists
try:
	os.makedirs(args.finished)
except OSError as exception:
	if exception.errno != errno.EEXIST:
		raise

# read the auphonic login-data file
with open(args.auphonic) as fp:
	auphonic_login = fp.read().strip().split(':', 1)


# Download the Events-Schedule and parse all Events out of it. Yield a tupel for each Event
def fetch_events():
	print('downloading pentabarf schedule')

	# destination list of events
	events = {}

	# download the schedule
	r = requests.get(args.schedule)

	# check HTTP-Response-Code
	if r.status_code != 200:
		print('download failed')
		return events

	# parse into ElementTree
	schedule = ET.fromstring(r.text.encode('utf-8'))

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



# an adapter which makes the multipart-generator issued by poster accessable to requests
# based upon code from http://stackoverflow.com/a/13911048/1659732
class IterableToFileAdapter(object):
	def __init__(self, iterable):
		self.iterator = iter(iterable)
		self.length = iterable.total

	def read(self, size=-1):
		return next(self.iterator, b'')

	def __len__(self):
		return self.length

# define a helper function simulating the interface of posters multipart_encode()-function
# but wrapping its generator with the file-like adapter
def multipart_encode_for_requests(params, boundary=None, cb=None):
	datagen, headers = multipart_encode(params, boundary, cb)
	return IterableToFileAdapter(datagen), headers

# tupload progress callback
def progress(param, current, total):
	sys.stderr.write("\ruploading {0}: {1:.2f}% ({2:d} MB of {3:d} MB)".format(param.filename if param else "", float(current)/float(total)*100, current/1024/1024, total/1024/1024))
	sys.stderr.flush()

# upload a single file to auphonic
def upload_file(filepath, event):
	print u"creating Auphonic-Production for Talk-ID {0} '{1}'".format(event['id'], event['title'])


	params = {
		# talk metadata
		"title": unicode(event['title']),
		"subtitle": unicode(event['subtitle']),
		"artist": unicode(event['personnames']),

		# prepend personnames to description (makes them searchable in youtube)
		"summary": unicode(event['personnames']) + "\n\n" + (unicode(event['description']) if event['description'] else unicode(event['abstract'])),

		# tell auphonic to start the production as soon as possible
		"action": "start",

		# file pointer to the input-file
		"input_file": open(filepath, 'rb')
	}

	# if a preset was specified on the command-line, apply it
	if args.preset:
		params['preset'] = args.preset

	# generate multipoart-encoder with progress display
	datagen, headers = multipart_encode_for_requests(params, cb=progress)

	# pass the generated encoder to requests which handles the http
	r = requests.post(
		'https://auphonic.com/api/simple/productions.json',
		auth=(auphonic_login[0], auphonic_login[1]),
		data=datagen,
		headers=headers
	)

	# linebreak
	print ""

	# check for success
	if r.status_code == 200:
		return True

	else:
		print "auphonic-upload failed with response: ", r, r.text
		return False


# initial download of the event-schedule
events = fetch_events()
eventsage = time()

# pattern to extract talk-.ids form filenames
pattern = re.compile("[0-9]+")

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

	if args.extension and os.path.splitext(filename)[1] != args.extension:
		continue

	# test if the filepath starts with a number and retrieve it
	print(u'found file {0} in recordings-folder'.format(filename))
	match = pattern.match(filename)

	# the filename does not start with a number
	if not match:
		print(u'"{0}" does not start with a number, skipping'.format(filename))

	else:
		# extract the number
		talkid = int(match.group(0))

		# test if the number is a valid talk-id
		if talkid in events:
			# extract the corresponding event from the shedule
			event = events[talkid]

			# upload that the file with the metadata found in the shedule
			if upload_file(filepath, event):
				print('done, moving to finished-folder')
				os.rename(filepath, os.path.join(args.finished, filename))

			else:
				print('upload FAILED! trying again, after the next Maus')


# wink bye-bye
print('all done, good night.')

