# get_email
Get imap or pop3 mail attachments matching an address and subject and save to file

Example usage: 

  python2 get_email.py  --server mail.server.com  -u mailuser -p password   -v 'address@domain'  -m  '.* anything'
  

Retrieve imap mail matching valid senders 'address@domain' and subject regular expression '.* attachment' and
save to file.  


Options:
-q/--quiet:  Quiet mod

-d/--delete: Delete message after saving


       
  
