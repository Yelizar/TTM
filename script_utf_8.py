from django.db import connection
cursor = connection.cursor()
results=[]
for row in cursor.fetchall(): results.append(row)
for row in results[1:]: cursor.execute('ALTER TABLE %s CONVERT TO CHARACTER SET utf8 COLLATE     utf8_general_ci;' % (row[0]))