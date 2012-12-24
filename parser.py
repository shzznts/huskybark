"""
To be coupled with huskybark.py
"""
from HTMLParser import HTMLParser

class FormParser(HTMLParser):
	"""Builds a dictionary of {name:value} pairs from the form elements of the fed html string.

	get_data() returns such dictionary
	"""
	def __init__(self):
		HTMLParser.__init__(self)
		self.reached_form = False
		self.data = {}
	def handle_starttag(self, tag, attrs):
		if tag == 'form':
			self.reached_form = True
		if self.reached_form and tag == 'input':
			name = ''
			value = ''
			for attr in attrs:
				if attr[0] == 'name': name = attr[1]
				if attr[0] == 'value': value = attr[1]
			self.data[name] = value
	def handle_endtag(self, tag):
		if tag == 'form':
			self.reached_form = False
	def get_data(self):
		return self.data

class SectionParser(HTMLParser):
	"""Looks through a course section html string and obtains the current available seats.

	get_seats_available() returns the number of seats currently available.
		If the number of seats available could not be obtained from the given html, 
		this method returns -1.
	"""
	def __init__(self):
		HTMLParser.__init__(self)
		self.seats_available = -1
		self.__reached_status = False
		self.__count = 0
	def handle_data(self, data):
		if data == 'Status':
			self.__reached_status = True
		elif self.__reached_status and self.__count < 3:
			self.__count += 1
		elif self.__reached_status and self.__count == 3:
			#Either data is seats available or '** Closed **'
			if data == '** Closed **':
				self.seats_available = 0
			else:
				self.seats_available = int(data)
			self.__count += 1
	def get_seats_available(self):
		return self.seats_available