#!/usr/bin/python
#create table devops(Id int AUTO_INCREMENT, Date varchar(100) NOT NULL, Sender varchar(255) NOT NULL, Subject varchar(255), Hash varchar(100) NOT NULL, PRIMARY KEY(Id));
import imaplib
import hashlib
import re
import mysql.connector

# Palabra a buscar
search_keyword = 'devops'

# Conectar con la DB local
db = mysql.connector.connect(user='root', password='root', host='127.0.0.1', database='ML')
curA = db.cursor(buffered=True)
curB = db.cursor(buffered=True)

# Conectarse a Gmail via protocolo IMAP 
mail = imaplib.IMAP4_SSL('imap.gmail.com',993)
# Credenciales
user = 'mispruebasml@gmail.com'
password = 'GruP0H1M42035.'
mail.login(user,password)
mail.select("INBOX")		#	Elegir buzon de entrada
result, data = mail.search(None, '(BODY "' + search_keyword + '")')		#Busca la palabra 'devops' usando el criterio IMAP: BODY
ids = data[0]		#	Lista de emails con la coincidencia

for email in ids.split():		#	Recorrer la lista de emails que tienen la coincidencia
	#	Obtener el cuerpo de mensaje para cada coincidencia
	result,data = mail.fetch(email, "(UID BODY[TEXT])")
	whole_message = data[0][1]
	#Look in the text of the body the keyword 'devops'
	#Previous search (BODY devops) included the keyword if it matched on the subject and was missing in the body
	#Using regex it's searched on the body only and ignoring capital letters.
	keyword = re.search(search_keyword, whole_message, re.IGNORECASE)
	#If devops is found in the body, extract From, Date and Subject
	if keyword:
		result, header = mail.fetch(email, '(UID BODY[HEADER])')
		From = re.search("From: .*",header[0][1], re.IGNORECASE)
		Date = re.search("Date: .*",header[0][1], re.IGNORECASE)
		Subject = re.search("Subject: .*",header[0][1], re.IGNORECASE)
		From = From.group(0).split(': ')[1].split('<')[1].split('>')[0].split('\r')[0]
		Date = Date.group(0).split(': ')[1].split('\r')[0]
		Subject = Subject.group(0).split(': ')[1].split('\r')[0]
		compiled = Date + From + Subject
		hash = hashlib.sha256(compiled).hexdigest()		# Hash identificador
		# Validar no existan datos
		validate = ("SELECT Id,Sender from devops WHERE Hash='" + hash + "'")
		curA.execute(validate)
		rows = curA.fetchall()
		if not rows:
			# Se crea query para meter info
			sql = "INSERT INTO devops (Date, Sender, Subject, Hash) VALUES (%s, %s, %s, %s)"
			val = (Date, From, Subject, hash)				# Se asignan datos a meter
			curB.execute(sql, val)		# Se mete la info
			print
			print "Email con la palabra '" + search_keyword + "' encontrada en el mail #" + email
			print "\t" + From + ": " + Subject + "   [" + Date + "]" 
			print "="*15 + " Nuevo Registro Insertado " + "="*30
		else:
			print "[+] Email viejo encontrado en la DB de <" + From + ">\t(Skipped)"
		db.commit()
###########################################################################################
