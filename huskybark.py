
# Copyright (C) 2012 Lincoln Sea - me@lincolnsea.com

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
# and associated documentation files (the "Software"), to deal in the Software without restriction, 
# including without limitation the rights to use, copy, modify, merge, publish, distribute, 
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software 
# is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or 
# substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""HuskyBark - course section availability tool for University of Washington registration.

Command-line tool that can be used to repeatedly retrieve the number of available seats
to a specific course lecture section, lab section, or quiz section.

Due to new UW security mods to registration, a valid UW NetID username and password are needed
to access time schedule classes and, therefore, is also needed by HuskyBark.

Recommended time between course checks is 6 seconds, which gives enough uncertainty to have
a successful section lookup. (UW registration security seems to disallow section lookups
separated by less than 5 seconds.)

Usage:
To start, use:
	python huskybark.py
To stop retrieving, use CTRL+C
"""

import urllib, urllib2, cookielib, time, getpass, sys
from parser import FormParser, SectionParser

LOGIN_URL = 'https://weblogin.washington.edu'
SECTION_URLBASE = 'https://sdb.admin.washington.edu/timeschd/uwnetid/sln.asp?'
RELAY_URL = 'https://sdb.admin.washington.edu/relay.pubcookie3?appsrvid=sdb.admin.washington.edu'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.11 ' + \
				'(KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11'

def parseForm(html):
	"""Returns a dictionary of {name:value} pairs from the form elements of the given html string."""
	parser = FormParser()
	parser.feed(html)
	return parser.get_data()

def retrieveSectionHTML(opener, sln, user, password, quarter):
	"""Returns the html of the course section's webpage as a string.

	opener - urllib.build_opener() instance with a cookie processor and a browser-like User-Agent
	sln - 'Section Listing Number' associated with a specific lecture section or quiz section
	user and password - UW NetID credentials
	quarter - time schedule quarter that the course is a part of
	"""
	login_data = {'user': user, 'pass': password}
	#Retrieve Form from Login Page
	html = opener.open(LOGIN_URL).read()
	post_params = parseForm(html)
	post_params.update(login_data)
	#Initial Login
	login_params = urllib.urlencode(post_params)
	opener.open(LOGIN_URL, login_params)
	#	***login cookies are now stored in cookiejar***
	#First Page: "You do not have Javascript enabled."
	section_url_params = urllib.urlencode({'SLN': sln, 'QTRYR': quarter})
	html = opener.open(SECTION_URLBASE + section_url_params).read()
	first_post_params = urllib.urlencode(parseForm(html))
	html = opener.open(LOGIN_URL, first_post_params).read()
	#Second Page: "You do not have Javascript turned on."
	second_post_params = urllib.urlencode(parseForm(html))
	return opener.open(RELAY_URL, second_post_params).read()

#Main
username = raw_input('What is your UW NetID?: ')
password = getpass.getpass('What is your password?: ')
quarter = raw_input('What quarter are the classes in? i.e. "WIN 2013": ').upper()
interval_length = int(raw_input('How many seconds between each check?: '))
if interval_length < 6:
	go_on = raw_input('Warning: less than 6 seconds between checks is unreliable. Continue? (y/n): ')
	if go_on and go_on.lower()[0] != 'y':
		sys.exit()
courses = []
course = int(raw_input('Enter course SLN (i.e. 10208): '))
while course:
	courses.append(course)
	course = raw_input('Enter another course SLN or press enter to continue: ')
	try:
		course = int(course)
	except Exception:
		break
while True:
	try:
		for course in courses:
			cj = cookielib.CookieJar()
			opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
			opener.addheaders = [('User-Agent', USER_AGENT)]
			parser = SectionParser()
			html = retrieveSectionHTML(opener, course, username, password, quarter)
			parser.feed(html)
			seats_available = int(parser.get_seats_available())
			if seats_available > 0:
				print('Course #' + str(course) + ' has ' + str(seats_available) + ' seat(s) available.')
			elif seats_available < 0:
				print('Course #' + str(course) + '\'s data is not available. ' + 
					'Check your credentials or choose a longer time between checks.')
			else:
				print('Course #' + str(course) + ' has no available seats.')
			time.sleep(interval_length)
	except KeyboardInterrupt:
		print('Thanks for using me!')
		sys.exit()