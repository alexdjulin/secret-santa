# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from pandas import read_csv  # read csv file
import os
import random
import re

## SCRPT VARIABLES TO EDIT ################################################################################################
csv_file = 'data/secret_santas_list.csv'
email_file = 'data/email.html'  # path to email contents (.txt for a plain text email, .html for html contents)
attempts_limit = 100  # while-exit condition: Number of attempts to assign secret santas
sg_sender_email = 'alexdjulin@gmail.com'
###########################################################################################################################

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
		to_print = "Secret Santa: {}   >>   Recipient: {}".format(self.name, self.recipient, self.recipient[1])
		return to_print

	def contact_secret_santa(self, subject, email_contents, email_format):
		""" send an email to recipient based on a subject and text/html content """

		# replace [NAME] and [RECIPIENT] tags by the current instance values in subject line and contents
		subject = subject.replace('[NAME]', self.name)
		subject = subject.replace('[RECIPIENT]', self.recipient)		
		email_contents = email_contents.replace('[NAME]', self.name)
		email_contents = email_contents.replace('[RECIPIENT]', self.recipient)
		
		try:
			# Retreive shotGrid API key from environment variables
			sg_key = os.environ.get('SENDGRID_API_KEY')

			# define email settings
			data = {
			"personalizations": [
				{
				"to": [
					{
					"email": self.email
					}
				],
				"subject": subject
				}
			],
			"from": {
				"email": sg_sender_email
			},
			"content": [
				{
				"type": "text/" + email_format,
				"value": email_contents
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

	# extract csv information, read empty cells as '' and not NaN
	df = read_csv(csv_file).fillna('')

	# store lists of names and emails
	names_list = list(df['Name'])
	email_list = list(df['Email'])

	# email validation (simple, just for typos)
	pattern = re.compile(r"^\S+@\S+\.\S+$")
	for email in email_list:
		if not re.match(pattern, email):
			raise ValueError("ERROR, {} is not a valid email address. Correct it or remove entry from csv file".format(email))

	# create list of SecretSanta instances
	secret_santas = []
	for i in range(len(df)):
		new_name = str(df['Name'][i])
		new_email = str(df['Email'][i])
		new_black_list = str(df['Black List'][i])
		new_santa = SecretSanta(name=new_name, email=new_email, black_list=new_black_list)
		secret_santas.append(new_santa)
	
	# assign recipients to santas
	# this loop will run as long as all assignements are not complete or if an attempts limit is reached (assignment considered not possible)
	counter = 0
	assignment_done = False # while-exit condition

	while not assignment_done and counter < attempts_limit:

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
				santa.recipient = new_recipient
				shuffled_list.remove(new_recipient)
		
	# assignment succeded
	if assignment_done:
		print("The Secret Santa assignment was successfull after {} attempts".format(counter+1))
	else:
		raise ValueError("The Secret Santa assignment was unsuccessfull after {} attempts. Black Lists incompatible. Increase the attempts limit or edit black lists".format(attempts_limit))
	
	# CONTACT SECRET SANTAS
	# get email format based on file extension
	email_format = 'html' if email_file.lower().endswith('html') else 'plain'

	# read email file and store contents: first line is the subject, the other lines the email contents
	with open(email_file, encoding='UTF-8') as f:
		email_lines = f.readlines()
		if len(email_lines) < 2:
			raise ValueError("Email contents should have at least 2 lines:\nLine 1: Email Subject\nLine 2: Email Contents")
		subject = email_lines[0]

		html_content = '\n'.join(email_lines[1:])

		# print santa and contact him per email
		for santa in secret_santas:
			print(santa)
			#santa.contact_secret_santa(subject, html_content, email_format)

## END OF MAIN ####