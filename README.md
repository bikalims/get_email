# get_email
Get imap or pop3 mail attachments matching an address and subject and save to file


usage: get_email.py [-h] [--quiet] [--pop3] --user USER --password PASSWORD
                    --server SERVER --valid VALID [VALID ...] --match MATCH
                    [MATCH ...] [--delete] [--ignore]
                    


Example: 

  python2 get_email.py  --server mail.server.com  -u mailuser -p password   -v 'address@domain'  -m  '.* attachment'
  

Retrieve imap mail matching valid senders 'address@domain' and matching subject using a regular expression,
eg. '.* attachment' and save to filename as specified in the mail. Files with the same name will be overwritten
by a later mail if found.


Other:
-q/--quiet:  Quiet mode

-d/--delete: Delete message after saving to file


 To delete both invalid and downloaded messages, use both -d and -i 
 
