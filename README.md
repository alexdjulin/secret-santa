# Secret Santa
Draw and email your Secret Santas using Python and Sendgrid... Ho ho ho! 🎅

## Description
This little script allows you to randomly draw and assign Secret Santas within a group of people. It offers the possibility to add a 'black list' too, i.e. a list of recipients that one Secret Santa should NOT have (in case of incompability, people not getting along with each other or similar reason). If the assignment is successful, Secret Santas will be notified per email and told who their recipient is. This way, no member of the group needs to be in charge of the assignment and know more than who his/her own recipient is.

## User input / Requirements
The input happens via a CSV file, where you can specify:
+ The name of the group members / string, mandatory
+ Their email / string, mandatory
+ A black list / string (group members names separated by a '|'), optional
