import random
import os
import sys
from shutil import copyfile

import smtplib

from email import generator
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email.header import Header
from email import encoders 

import cyrtranslit

#get recipient's address
emlto = str(sys.argv[1])
print(emlto)
cmpnnm = "ООО \"ТЕСТ\""
## You MUST create your own template files of types below ##
attch_fl_tmplt = "tmplt"
fl_tps_arr = ["docx","pdf","doc"]

#working dirs
sttngsdir = os.path.join(os.getcwd(), "params")
gendir = os.path.join(os.getcwd(), "generated")

#DBG
cnsldbg = 1
genfile = 1
sendmsg = 0

## create your own mail_server_creds.ini in settings dir ##
smtp_creds = []
## server\n username\n pass\n ##


def gen_email_addr(frm):
	
	frm_addr_frst = ['info','process','warning','vzyskanie','shtraf','dolg','alarm',
					'zapros','request','tax','nedoimka','uvedomlenie']
	frm_dmns = ['com','net','ru','org']
	addr = random.choice(frm_addr_frst).rstrip()
	tmp = frm.replace('"','')
	if any(c in frm for c in ("суд", "Суд")):
		tmp = cyrtranslit.to_latin(tmp,'ru')
		tmp = tmp.replace("'",'')
		tmp = tmp.split(' ')
		i = 0
		for s in tmp:
			tmp[i] = s[:1].lower()
			i+=1
		addr +="@"+''.join(tmp).rstrip()+".court.gov.ru"
	elif any(c in frm for c in ("инспекция", "ИФНС")):
		addr +="@ifns"+frm.rstrip()[-2:]+".gov.ru"
	elif any(c in frm for c in ("банк", "Банк")):
		tmp = cyrtranslit.to_latin(tmp,'ru').lower()
		tmp = tmp.replace("'",'')
		if tmp[:4] == "bank":
			tmp = tmp.split(tmp[:4],1)[1]
		addr +="@"+tmp.replace(' ','').rstrip()+"."+random.choice(frm_dmns)
	else:
		tmp = cyrtranslit.to_latin(tmp,'ru').lower()
		tmp = tmp.replace("'",'')
		addr +="@"+tmp.replace(' ','').rstrip()+"."+random.choice(frm_dmns)
	return addr


def gen_eml(frm,subj,text,attch):
	
	html_data = text

	msg = MIMEMultipart('mixed')
	msg['Subject'] = subj
	msg['From'] = formataddr((frm,gen_email_addr(frm)))
	msg['To'] = emlto
	#msg['Reply-To'] = formataddr((frm,gen_email_addr(frm)))
	
	part = MIMEText(html_data, 'plain')
	msg.attach(part)
	
	# open the file to be sent  
	filename = attch
	#flnmencdd = encode("MIME-Q",filename)
	attachment = open(attch, "rb") 
	  
	# instance of MIMEBase and named as p 
	p = MIMEBase('application', 'binary')  #; name= % filename
	  
	# To change the payload into encoded form 
	p.set_payload((attachment).read()) 
	  
	# encode into base64 
	encoders.encode_base64(p) 
	
	#FILENAME=FILENAME WO BRACKETS OR OTHER SIGNS AND THEY ARE DIFFERENT FILENAMES!
	p.add_header('Content-Disposition', 'attachment', filename=filename) 
	  
	# attach the instance 'p' to instance 'msg' 
	msg.attach(p) 
	
	if sendmsg:
		server = smtplib.SMTP_SSL(smtp_creds[0].rstrip(), 465)
		server.login(smtp_creds[1].rstrip(), smtp_creds[2].rstrip())
		server.set_debuglevel(0)
		server.sendmail( formataddr((frm,gen_email_addr(frm))), emlto, msg.as_string() )
		server.quit()
	
	if genfile:
		cwd = os.getcwd()
		msgnm = "tstmsg"+f'{random.randrange(100,999999,1)}'+".eml"
		outfile_name = os.path.join(cwd, msgnm)
		with open(outfile_name, 'w') as outfile:
			gen = generator.Generator(outfile)
			gen.write(msg.as_string())


def count_lines(filename, chunk_size=1<<13):
	with open(filename, encoding='utf-8-sig') as file:
		return sum(chunk.count('\n')
			for chunk in iter(lambda: file.read(chunk_size), ''))

			
def get_line_n(filename,n):
	with open(filename, encoding='utf-8-sig') as file:
		i = 0
		for line in file:
			if i == n:
				return line
			i+=1

			
def get_rand_phrase(file):
	return(get_line_n(file, random.randrange(count_lines(file))))


## MAIN PROCEDURE START ##

os.chdir(sttngsdir)

#get smtp server settings	
with open("mail_server_creds.ini", encoding='utf-8-sig') as f:
	smtp_creds = f.readlines()

#generate sender
frm = get_rand_phrase("from.txt")
if "CmpNmF" in frm:
	frm = frm.replace("CmpNmF", "\"" + get_rand_phrase("cmpnnms.txt").rstrip() + "\"")
if "ONum" in frm:
	frm = frm.replace("ONum", str(random.randrange(2,48,1)))	
if "Суд" in frm:
	frm = frm.replace("Суд", get_rand_phrase("courts.txt").rstrip())
if "Банк" in frm:
	frm = frm.rstrip() + " \"" + get_rand_phrase("banks.txt").rstrip() + "\""

subj = get_rand_phrase("subj.txt").replace("CmpNm",cmpnnm)

#generate message body
msgbody = ""
with open("msg.txt", encoding='utf-8-sig') as file:
	i = 0
	fllns = (count_lines("msg.txt") - 1)
	for line in file:
		n = len(line.split("/"))
		str = (line.split("/"))[random.randrange(n)]
		if i == 0:
			msgbody += str
		elif i == fllns:
			msgbody = msgbody.replace("From",frm).replace("  "," ").replace("CmpNm",cmpnnm)
			msgbody += str
		else:
			msgbody += (str.rstrip() + " ")
		i+=1

if cnsldbg:
	print("From:")
	print(frm)
	print("Subj:")
	print(subj)
	print("Text:")
	print(msgbody)

#creating attachments		
fltp = random.choice(fl_tps_arr)
flnm = get_rand_phrase("flnms.txt").rstrip()
copyfile(attch_fl_tmplt + "." + fltp, os.path.join(gendir,flnm + "." + fltp))

os.chdir(gendir)

#modify file size by adding random amount of zeroes to file's end
#this breaks docx
if fltp != "docx":
	with open(flnm + "." + fltp, 'r+b') as file:
		fcontent = file.read()
	os.remove(flnm + "." + fltp)
	n = (random.randrange(2,600,1)) * 1000
	byte_arr = [0] * n
	binary_format = bytearray(byte_arr)
	with open(flnm + "." + fltp, 'w+b') as file:
		file.write(fcontent + binary_format)

#creating eml
gen_eml(frm,subj,msgbody,(flnm + "." + fltp))



