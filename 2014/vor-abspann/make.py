#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import glob
import os
import re
import errno
import unicodedata
import urllib2
import xml.etree.ElementTree as ET
import textwrap

fps = 25

reload(sys)
sys.setdefaultencoding('utf-8')

# t: current time, b: begInnIng value, c: change In value, d: duration
def easeOutCubic(t, b, c, d):
	t=float(t)/d-1
	return c*((t)*t*t + 1) + b

def ensure_path_exists(path):
	try:
		os.makedirs(path)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

def ensure_files_removed(files):
	for f in glob.glob(files):
		os.unlink(f)

def slugify(value):
	"""
	Normalizes string, converts to lowercase, removes non-alpha characters,
	and converts spaces to hyphens.
	"""
	value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
	value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
	value = unicode(re.sub('[-\s]+', '-', value))
	return value




def abspannFrames():
	# 5 Sekunden

	# 2 Sekunden Fadein Text
	frame = 0
	frames = 2*fps
	for i in range(0, frames):
		yield (frame+i, easeOutCubic(i, 0, 1, frames), 0)

	# 2 Sekunde Fadein Lizenz-Logo
	frame = frame+i+1
	frames = 2*fps
	for i in range(0, frames):
		yield (frame+i, 1, float(i)/frames)

	# 1 Sekunde stehen bleiben
	frame = frame+i+1
	frames = 1*fps
	for i in range(0, frames):
		yield (frame+i, 1, 1)

def vorspannFrames():
	# 7 Sekunden

	# 2 Sekunden Text 1
	frame = 0
	frames = 2*fps
	for i in range(0, frames):
		yield (frame+i, easeOutCubic(i, 0, 1, frames), easeOutCubic(i, 0, 1, frames), 0)

	# 1 Sekunde Fadeout Text 1
	frame = frame+i+1
	frames = 1*fps
	for i in range(0, frames):
		yield (frame+i, 1, 1-(float(i)/frames), 0)

	# 2 Sekunden Text 2
	frame = frame+i+1
	frames = 2*fps
	for i in range(0, frames):
		yield (frame+i, 1, 0, easeOutCubic(i, 0, 1, frames))

	# 2 Sekunden stehen bleiben
	frame = frame+i+1
	frames = 2*fps
	for i in range(0, frames):
		yield (frame+i, 1, 0, 1)



def abspann(lizenz):
	print "erzeuge Abspann"
	filename = '../abspann-{0}.mp4'.format(lizenz)

	os.chdir('artwork')
	ensure_path_exists('.frames')

	with open('abspann.svg', 'r') as abspann_file:
		abspann = abspann_file.read()

	for (frameNr, opacity, opacityLizenz) in abspannFrames():
		print "frameNr {0:2d} => opacity {1:0.2f}, opacityLizenz {2:0.2f}".format(frameNr, opacity, opacityLizenz)

		pairs = \
			('%opacityLizenz', str(opacityLizenz)), \
			('%opacity', str(opacity)), \
			('%lizenz', lizenz)

		with open('.gen.svg', 'w') as gen_file:
			gen_abspann = reduce(lambda a, kv: a.replace(*kv), pairs, abspann)
			gen_file.write( gen_abspann )

		os.system('rsvg-convert .gen.svg > .frames/{0:04d}.png'.format(frameNr))

	ensure_files_removed(filename)
	os.system('avconv -f image2 -i .frames/%04d.png -c:v libx264 -preset veryslow -qp 0 "'+filename+'"')

	print "aufräumen"
	ensure_files_removed('.frames/*.png')
	os.rmdir('.frames')
	ensure_files_removed('.gen.svg')
	os.chdir('..')

def vorspann(id, title, personnames):
	print u'erzeuge Vorspann für {0:4d} ("{1}")'.format(id, title)
	filename = u'../{0:04d}-{1}.mp4'.format(id, slugify(unicode(title)) )

	os.chdir('artwork')
	ensure_path_exists('.frames')

	with open('vorspann.svg', 'r') as vorspann_file:
		vorspann = vorspann_file.read()

	# svg does not have a method for automatic line breaking, that rsvg is capable of
	# so we do it in python as good as we can
	breaktitle = '</tspan><tspan x="150" dy="45">'.join(textwrap.wrap(title, 35))

	for (frameNr, opacityBox, opacity1, opacity2) in vorspannFrames():
		print "frameNr {0:2d} => opacityBox {1:0.2f}, opacity1 {2:0.2f}, opacity2 {3:0.2f}".format(frameNr, opacityBox, opacity1, opacity2)

		pairs = \
			('%opacity1', str(opacity1)), \
			('%opacity2', str(opacity2)), \
			('%opacityBox', str(opacityBox)), \
			('%id', str(id)), \
			('%title', breaktitle), \
			('%personnames', personnames)

		with open('.gen.svg', 'w') as gen_file:
			gen_vorspann = reduce(lambda a, kv: a.replace(*kv), pairs, vorspann)
			gen_file.write( gen_vorspann )

		os.system('rsvg-convert .gen.svg > .frames/{0:04d}.png'.format(frameNr))

	ensure_files_removed(filename)
	os.system(u'avconv -f image2 -i .frames/%04d.png -c:v libx264 -preset veryslow -qp 0 "'+filename+'"')

	print "aufräumen"
	ensure_files_removed('.frames/*.png')
	os.rmdir('.frames')
	ensure_files_removed('.gen.svg')
	os.chdir('..')


def events():
	print "downloading pentabarf program"
	response = urllib2.urlopen('http://www.fossgis.de/konferenz/2014/programm/schedule.de.xml')
	xml = response.read()
	schedule = ET.fromstring(xml)
	#schedule = ET.parse('schedule.de.xml')

	for day in schedule.iter('day'):
		date = day.get('date')
		for room in day.iter('room'):
			for event in room.iter('event'):
				personnames = []
				for person in event.find('persons').iter('person'):
					personnames.append(person.text)

				yield ( int(event.get('id')), event.find('title').text, ', '.join(personnames) )

#for (id, title, personnames) in events():
#	vorspann(id, title, personnames)

#vorspann(667, 'OpenJUMP - Überblick, Neuigkeiten, Zusammenarbeit/Schnittstellen mit proprietärer Software', 'Matthias Scholz')
#vorspann(754, 'Eröffnung', '')
#vorspann(760, 'Was ist Open Source, wie funktioniert das und worauf muss man achten', 'Arnulf Christl, Athina Trakas')
abspann('by-sa')
abspann('by-nc-sa')
abspann('cc-zero')
