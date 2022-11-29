#!/usr/bin/env python
"""
get_email.py - Designed to be run from cron, this script checks the pop3 mailbox
Based on django-helpdesk's get_email.py. inus@bikalabs.com 2022-10-17

Live params:
python get_email.py --user zzzz --server pop.zzzz.com --pop3 --password zzzz --valid NoReply@zzzz.com.zzzz --match '.* lims' --file_path '/home/zzzz/sync/current'
"""
from __future__ import print_function

import email
import imaplib
import mimetypes
import poplib
import re
import sys
import argparse

from email.header import decode_header
from email.utils import parseaddr, collapse_rfc2231_value

months_conversion = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dev": "12",
}


def process_imap(args):
    server = imaplib.IMAP4_SSL(args.server)
    server.login(args.user, args.password)
    server.select("INBOX")
    status, data = server.search(None, "NOT", "DELETED")
    if not args.quiet:
        print(
            "Info: imap login to {} as {}, {} messages \n".format(
                args.server, args.user, len(data[0].split())
            )
        )
    if data:
        msgnums = data[0].split()
        for num in msgnums:
            status, data = server.fetch(num, "(RFC822)")
            if file_from_message(message=data[0][1], quiet=args.quiet) and args.delete:
                server.store(num, "+FLAGS", "\\Deleted")
                if not args.quiet:
                    print("Info: Message #{} deleted ".format(num))

    server.expunge()
    server.close()
    server.logout()


def process_pop3(args):
    server = poplib.POP3_SSL(args.server)
    server.getwelcome()
    response = server.user(args.user)
    response = server.pass_(args.password)
    response, messagesInfo, octets = server.list()

    if not args.quiet:
        print(
            "Info: pop3 login to {} as {}, {} messages \n".format(
                args.server, args.user, len(messagesInfo)
            )
        )
    file_path = "."
    if args.file_path:
        file_path = args.file_path
        if type(file_path) == list and len(file_path) == 1:
            file_path = file_path[0]
    for msg in messagesInfo:
        try:  # Sometimes messages are in bytes???
            msg = msg.decode("utf-8")
        except Exception:
            pass  # wasn't necessary
        try:
            msgNum = int(msg.split(" ")[0])
            # msgSize = int(msg.split(" ")[1])

            response, message_lines, octets = server.retr(msgNum)
            for i in range(len(message_lines)):  # in case message is binary
                try:
                    message_lines[i] = message_lines[i].decode("utf-8")
                except Exception:
                    pass

            if sys.version_info < (3,):
                full_message = "\n".join(message_lines)
            else:
                full_message = "\n".join(message_lines).encode()
            if file_from_message(
                message=full_message, file_path=file_path, quiet=args.quiet
            ):
                if args.delete:
                    server.dele(msgNum)
                    sys.stderr.write("Deleted message # {}\n".format(msgNum))
                else:
                    sys.stderr.write(
                        "Message #{} not deleted, -d not specified\n".format(msgNum)
                    )
            else:
                sys.stderr.write(
                    "File not saved, message #{} not deleted\n".format(msgNum)
                )

        except Exception as e:
            sys.stderr.write(
                "Error: Exception process_email, message #{}, {}\n".format(msg, e)
            )


def decodeUnknown(charset, string):
    if not charset:
        try:
            return string.decode("UTF_8", "ignore")
        except Exception:
            try:
                return string.decode("iso8859-1", "ignore")
            except Exception:
                return string
    try:
        return str(string, charset)
    except Exception:
        try:
            return bytes(string, "UTF_8")
        except Exception:
            return string.decode("UTF_8", "ignore")


def decode_mail_headers(string):
    decoded = decode_header(string)
    return decoded[0][0]


def file_from_message(message, file_path=".", quiet=False):
    # 'message' must be an RFC822 formatted message.
    msg = message

    if sys.version_info < (3,):
        message = email.message_from_string(msg)
    else:
        message = email.message_from_string(msg.decode())

    subject = message.get("subject", "No subject.")
    subject = decode_mail_headers(decodeUnknown(message.get_charset(), subject))
    subject = str(subject)
    sender = message.get("from", "Unknown Sender")
    sender = decode_mail_headers(decodeUnknown(message.get_charset(), sender))

    try:  # in case it's binary. Seems like sometimes it is and sometimes it isn't :-/
        sender = sender.decode("utf-8")
    except Exception:
        pass

    sender_email = "".join(parseaddr(sender)[1])

    body_plain = ""
    for s in Xargs.valid:
        try:
            re.match(s, sender_email)
        except Exception:
            sys.stderr.write(
                'Invalid regular expression "{}" for sender {}, subject "{}".\n'.format(
                    s, sender_email, subject
                )
            )
            return False

        if not re.match(s, sender_email):
            sys.stderr.write(
                'Ignoring mail from {}. Subject "{}".\n'.format(sender, subject)
            )
            if Xargs.ignore:
                return True  # and delete
            else:
                return False
        else:
            sys.stderr.write('Sender match: "{}".\n'.format(sender))
    for s in Xargs.match:
        try:
            matchobj = re.match(s, subject)
        except Exception:
            sys.stderr.write(
                'Invalid regular expression "{}" for sender {}, subject "{}".\n'.format(
                    s, sender, subject
                )
            )
            return False
        if matchobj:
            if not quiet:
                sys.stderr.write('Subject match: "{}".\n'.format(matchobj.string))

            counter = 0
            files = []

            for part in message.walk():
                if part.get_content_maintype() == "multipart":
                    continue

                name = part.get_param("name")
                if name:
                    name = collapse_rfc2231_value(name)

                if part.get_content_maintype() == "text" and name is None:
                    if part.get_content_subtype() == "plain":
                        body_plain = decodeUnknown(
                            part.get_content_charset(), part.get_payload(decode=True)
                        )
                    else:
                        # TODO - what happens with html
                        part.get_payload(decode=True)
                else:
                    if not name:
                        ext = mimetypes.guess_extension(part.get_content_type())
                        name = "part-%i%s" % (counter, ext)

                if (
                    part.get_content_maintype() == "text"
                    and part.get_content_subtype() == "csv"
                ):
                    files.append(
                        {
                            "filename": name,
                            "content": part.get_payload(decode=True),
                            "type": part.get_content_type(),
                        },
                    )

                counter += 1

            if body_plain:
                body = body_plain
            else:
                body = "No plain-text email body"
            sys.stderr.write(f"Body test: {body}")
            for file in files:
                if file["content"]:  # and file['filename']:
                    if file["filename"]:
                        if sys.version_info < (3,):
                            filename = (
                                file["filename"]
                                .encode("ascii", "replace")
                                .replace(" ", "_")
                            )
                        else:
                            filename = file["filename"].replace(" ", "_")

                        filename = file["filename"].replace(" ", "_")
                        filename = re.sub("[^a-zA-Z0-9._-]+", "", filename)
                        if False:  # Add date stamp to file names
                            parts = filename.split(".")
                            if parts and parts[-1] == "csv":
                                date = message.get("Date").split(" ")
                                date = f"{date[2]}{months_conversion[date[1]]}{int(date[0]):02d}"
                                parts.insert(-1, date)
                                filename = f"{'.'.join(parts)}"
                        filename = f"{file_path}/{filename}"
                        try:
                            f = open(filename, "w")

                            if sys.version_info < (3,):
                                f.write(file["content"])
                            else:
                                f.write(file["content"].decode())

                            f.close()
                        except Exception as e:
                            sys.stderr.write(
                                "Error: Attachment not saved: {}, error {}\n".format(
                                    filename, e
                                )
                            )
                            return False
                        if not quiet:
                            sys.stderr.write(
                                "Attachment saved as {}\n".format(filename)
                            )
            return True


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Retrieve email attachments.")
    parser.add_argument(
        "--quiet",
        "-q",
        default=False,
        action="store_true",
        help="Hide details about each queue/message as they are processed",
    )
    parser.add_argument(
        "--pop3",
        "-3",
        default=False,
        action="store_true",
        help="Use POP3 instead of IMAP",
    )
    parser.add_argument("--user", "-u", required=True, type=str)
    parser.add_argument("--password", "-p", required=True)
    parser.add_argument(
        "--server", "-s", required=True, type=str, help="Mail server address"
    )
    parser.add_argument(
        "--valid",
        "-v",
        required=True,
        type=str,
        help="Valid sender emails, eg user@site.com",
        nargs="+",
    )
    parser.add_argument(
        "--match",
        "-m",
        required=True,
        type=str,
        help='Valid subject, eg "(.)* lims"',
        nargs="+",
    )
    parser.add_argument(
        "--file_path",
        "-fp",
        required=False,
        type=str,
        help="Path for saving files",
        nargs="+",
    )
    parser.add_argument(
        "--delete",
        "-d",
        default=False,
        action="store_true",
        help="Delete mail after saving",
    )
    parser.add_argument(
        "--ignore",
        "-i",
        default=False,
        action="store_true",
        help="Delete ignored mail after saving",
    )
    Xargs = parser.parse_args()

    if Xargs.pop3:
        process_pop3(Xargs)
    else:
        process_imap(Xargs)
