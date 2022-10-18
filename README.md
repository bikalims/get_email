# get_email.py

Get imap or pop3 mail attachments matching an address and subject and save to file

```
usage: get_email.py [-h] [--quiet] [--pop3] --user USER --password PASSWORD
                    --server SERVER --valid VALID [VALID ...] --match MATCH
                    [MATCH ...] [--delete] [--ignore]
```
  
## Retrieve imap or pop3 secure mail,
  1. matching valid senders 'address@domain'
   and 
  2. matching subject, using a regular expression

eg. '.* attachment' and save to filename as specified in the mail. 
Files with the same name will be overwritten by a later mail if found.

## Switches:
```
-q/--quiet:  Quiet mode

-d/--delete: Delete message after saving to file

-i/--ignore: Also delete ignored messages
```

## Matching by email address and subject:

# Example 1: keyword "lims" in middle of subject field, match sender at beginning

```
python get_email.py  --server mail.example.com  -u user  -p password123   -v 'NoReply@sample'  -m '.* lims' 

Info: imap login to mail.example.com as user, 5 messages

Ignoring mail from John Smith <john.smith@gmail.com>. Subject "lims".
Sender match: "NoReply@sample.com".
Subject match: "Account lims was executed at 10/18/2022 4:00:07 PM".
Attachment saved as Account_lims.csv
```

# Example 2: Sender match at beginning, subject at beginning (multiple attachments in one message)

```
python get_email.py  --server mail.example.com  -u user -p password123   -v 'john'  -m 'lims'

Sender match: "John Smith <john.smith@gmail.com>".
Subject match: "lims".
Attachment saved as system_lims.csv
Attachment saved as attention_contact_lims.csv
Attachment saved as location_lims.csv
Attachment saved as Account_lims.csv
Ignoring mail from NoReply@sample.com Subject "Account lims was executed at 10/18/2022 4:00:07 PM".
Ignoring mail from NoReply@sample.com Subject "attention contact lims was executed at 10/18/2022 4:10:03 PM".
Ignoring mail from NoReply@sample.com Subject "location lims was executed at 10/18/2022 4:20:00 PM".
Ignoring mail from NoReply@sample.com Subject "system lims was executed at 10/18/2022 4:30:06 PM".
```

## Deleting mail messages

 To delete both invalid and downloaded messages, use both -d and -i 
 
