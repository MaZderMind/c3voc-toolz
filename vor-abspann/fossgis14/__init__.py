#!/usr/bin/python
# -*- coding: UTF-8 -*-

# URL to Schedule-XML
scheduleUrl = 'http://www.fossgis.de/konferenz/2014/programm/schedule.de.xml'

# For (really) too long titles
titlemap = {
	708: "Neue WEB-Anwendungen des LGRB Baden-Württemberg im Überblick"
}


def outroFrames():
	# 5 Sekunden

	# 2 Sekunden Fadein Text
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('banderole', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames) ),
			('license', 'style', 'opacity', 0)
		)

	# 2 Sekunde Fadein Lizenz-Logo
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('banderole', 'style', 'opacity', 1),
			('license', 'style', 'opacity', "%.4f" % (float(i)/frames))
		)

	# 1 Sekunde stehen bleiben
	frames = 1*fps
	for i in range(0, frames):
		yield (
			('banderole', 'style', 'opacity', 1),
			('license', 'style', 'opacity', 1)
		)

def introFrames():
	# 7 Sekunden

	# 2 Sekunden Text 1
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('box',   'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames)),
			('url',   'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames)),
			('text1', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames)),
			('text2', 'style', 'opacity', 0)
		)

	# 1 Sekunde Fadeout Text 1
	frames = 1*fps
	for i in range(0, frames):
		yield (
			('box',   'style', 'opacity', 1),
			('url',   'style', 'opacity', 1),
			('text1', 'style', 'opacity', "%.4f" % (1-(float(i)/frames))),
			('text2', 'style', 'opacity', 0)
		)

	# 2 Sekunden Text 2
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('box',   'style', 'opacity', 1),
			('url',   'style', 'opacity', 1),
			('text1', 'style', 'opacity', 0),
			('text2', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames))
		)

	# 2 Sekunden stehen bleiben
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('box',   'style', 'opacity', 1),
			('url',   'style', 'opacity', 1),
			('text1', 'style', 'opacity', 0),
			('text2', 'style', 'opacity', 1)
		)

def pauseFrames():
	# 12 Sekunden

	# 2 Sekunden Text1 stehen
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('text1', 'style', 'opacity', 1),
			('text2', 'style', 'opacity', 0)
		)

	# 2 Sekunden Fadeout Text1
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('text1', 'style', 'opacity', "%.4f" % (1-easeOutCubic(i, 0, 1, frames))),
			('text2', 'style', 'opacity', 0)
		)

	# 2 Sekunden Fadein Text2
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('text1', 'style', 'opacity', 0),
			('text2', 'style', 'opacity', "%.4f" % easeOutCubic(i, 0, 1, frames))
		)

	# 2 Sekunden Text2 stehen
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('text1', 'style', 'opacity', 0),
			('text2', 'style', 'opacity', 1)
		)

	# 2 Sekunden Fadeout Text2
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('text1', 'style', 'opacity', 0),
			('text2', 'style', 'opacity', "%.4f" % (1-easeOutCubic(i, 0, 1, frames)))
		)

	# 2 Sekunden Fadein Text1
	frames = 2*fps
	for i in range(0, frames):
		yield (
			('text1', 'style', 'opacity', "%.4f" % (easeOutCubic(i, 0, 1, frames))),
			('text2', 'style', 'opacity', 0)
		)

def debug():
	render(
		'intro.svg',
		'../intro.dv',
		introFrames,
		{
			'$id': 667,
			'$title': 'OpenJUMP - Überblick, Neuigkeiten, Zusammenarbeit/Schnittstellen mit proprietärer Software',
			'$subtitle': 'Even more news about OpenJUMP',
			'$personnames': 'Matthias Scholz'
		}
	)

	render(
		'outro.svg',
		'../outro.dv',
		outroFrames
	)

	render('pause.svg',
		'../pause.dv',
		pauseFrames
	)

def tasks(queue):
	# iterate over all events extracted from the schedule xml-export
	for event in events():

		# generate a task description and put them into the queue
		queue.put((
			'intro.svg',
			str(event['id'])+".dv",
			introFrames,
			{
				'$id': event['id'],
				'$title': event['title'],
				'$subtitle': event['subtitle'],
				'$personnames': event['personnames']
			}
		))

	# place a task for the outro into the queue
	queue.put((
		'outro.svg',
		'outro.dv',
		outroFrames
	))

	# place the pause-sequence into the queue
	queue.put((
		'pause.svg',
		'pause.dv',
		pauseFrames
	))
