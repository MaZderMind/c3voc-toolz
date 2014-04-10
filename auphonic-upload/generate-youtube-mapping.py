#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re
import json
import argparse
import requests

parser = argparse.ArgumentParser(description='Fetch finished Auphonic-Productions from Auphonic and parse all Youtube-Urls out, order them by talk-id and resturn a mapping-json')

parser.add_argument('--auphonic-login',
	dest='auphonic',
	default=os.path.expandvars('$HOME/.auphonic-login'),
	help='path of a file containing "username:password" of your auphonic account')

args = parser.parse_args()

# try to read the auphonic login-data file
with open(args.auphonic) as fp:
	auphonic_login = fp.read().strip().split(':', 1)

r = requests.get(
	'https://auphonic.com/api/simple/productions.json',
	auth=(auphonic_login[0], auphonic_login[1])
)

if r.status_code != 200:
	print "fetching productions failed with response: ", r, r.text
	sys.exit(1)

productions = r.json()
urls = {}

if productions['data']:
	for production in productions['data']:
		for service in production['outgoing_services']:
			if service['type'] == 'youtube' and service['result_page']:
				talkid = int( re.match('[0-9]+', production['input_file']).group(0) )
				urls[talkid] = service['result_page']

print json.dumps(urls, indent=4)
