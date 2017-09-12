import connectdb as cdb


db = cdb.Db().connection()

sql="select id, cgst,sgst, net from bill where date > '2017-6-30' ;"

cur=db.cursor()
cur.execute(sql)
rows=cur.fetchall()
for r in rows:
	net=r[3]
	id=r[0]
	gst=net*6/112
	sql = 'update bill set cgst=%s, sgst=%s where id=%s;'
	cur.execute(sql,(gst,gst,id))
db.commit()


sql="update stock set sgstp=%s , cgstp=%s where cur_count>0;"
cur.execute(sql,(6,6))
db.commit()
	

