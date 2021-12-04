# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from pandas import read_csv  # read csv file
import random

class SecretSanta:

	def __init__(self, name, email, black_list = None):
		""" constructor """
		self.name = name
		self.email = email 
		self.recipient = None  # will be allocated later
		# defining black list
		self.black_list = list()
		self.black_list.append(self.name)  # adding own name to black list
		if black_list: # adding optional names if passed
			self.black_list += black_list.split('|')

	def __repr__(self):
		""" print your secret santa object """
		#to_print = "Name: {}\nEmail: {}\nRecipient: {}\nBlack List: {}\n".format(self.name, self.email, self.recipient, self.black_list)
		to_print = "Secret Santa: {}   >>   Recipient: {} ({})".format(self.name, self.recipient[0], self.recipient[1])
		return to_print

	def contact_secret_santa(self, subject, html_content, format):
		""" send an email to recipient based on a subject and html content """

		# replace [NAME] and [RECIPIENT] tags by the current instance values in subject line and html contents
		subject = subject.replace('[NAME]', self.name)
		subject = subject.replace('[RECIPIENT]', self.recipient[0])		
		html_content = html_content.replace('[NAME]', self.name)
		html_content = html_content.replace('[RECIPIENT]', self.recipient[0])
		
		message = Mail(self.email, self.recipient[1], subject, html_content)

		try:
			# ShotGrid API key (Private, don't share!)
			sg_key = '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'
			# define email settings
			data = {
			"personalizations": [
				{
				"to": [
					{
					"email": self.recipient[1]
					}
				],
				"subject": subject
				}
			],
			"from": {
				"email": self.email
			},
			"content": [
				{
				"type": "text/" + format,
				"value": html_content
				}
			]
			}
			sg = SendGridAPIClient(sg_key)
			response = sg.client.mail.send.post(request_body=data)
			# print(response.status_code)
			# print(response.body)
			# print(response.headers)
			print("Secret Santa {} has been notified per E-Mail.".format(self.name))
		except Exception as e:
			print(e)
			print(e.body)

## MAIN ####
if __name__ == '__main__':

	# extract csv information to lists (reads empty cells as '' and not NaN)
	csv_file = 'secret_santas_list.csv'
	df = read_csv(csv_file).fillna('')
	names_list = list(df['Name'])
	email_list = list(df['Email'])

	# create list of SecretSanta instances
	secret_santas = []
	for i in range(len(df)):
		new_name = str(df['Name'][i])
		new_email = str(df['Email'][i])
		new_black_list = str(df['Black List'][i])
		new_santa = SecretSanta(name=new_name, email=new_email, black_list=new_black_list)
		secret_santas.append(new_santa)
	

	# assign recipients to santas
	# this loop will run as long as all assignements are not complete or if an attempts limit is reched (assignment not possible)
	counter = 0
	counter_limit = 100 # attempts limit
	assignment_done = False # while-exit condition

	while not assignment_done and counter < counter_limit:

		# delete any recipients and reset assignment done
		for santa in secret_santas:
			santa.recipient = ''
		assignment_done = True

		# shuffle the list of names
		random.seed()
		shuffled_list = random.sample(names_list, k=len(names_list))
		
		# go through all secret santas
		for santa in secret_santas:
			allowed_recipients = [name for name in shuffled_list if name not in santa.black_list]
			# if no recipient available, start a new loop with a different shuffled list
			if not allowed_recipients:
				# print("No recipient found for {}".format(santa.name))
				assignment_done = False
				counter += 1
			else:
				# set recipient and remove it from the list
				new_recipient = random.choice(allowed_recipients)
				santa.recipient = new_recipient, email_list[names_list.index(new_recipient)]
				shuffled_list.remove(new_recipient)
		
	# assignment succeded
	if assignment_done:
		print("The Secret Santa assignment was successfull after {} attempts".format(counter))
	else:
		raise ValueError("The Secret Santa assignment was unsuccessfull after {} attempts. Black Lists incompatible. Increase the attempts limit or edit black lists".format(counter_limit))
	
	# CONTACT SECRET SANTAS
	# read email file and store contents: first line is the subject, the other lines the email contents
	mail_path = 'email.html'
	format = 'html' if mail_path.lower().endswith('html') else 'plain'

	with open(mail_path) as f:
		email_lines = f.readlines()
		if len(email_lines) < 2:
			raise ValueError("Email contents should have at least 2 lines:\nLine 1: Email Subject\nLine 2: Email Contents")
		subject = email_lines[0]
		html_content = '\n'.join(email_lines[1:])

		# send email to secret santas
		for santa in secret_santas[:1]:
			print(santa)
			santa.contact_secret_santa(subject, html_content, format)
		