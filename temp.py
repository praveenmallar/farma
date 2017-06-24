import connectdb as cdb
import datetime as dt

fil = open ("aaa.csv")
lines= fil.readlines()
st=[]
for l in lines:
	fs=l.split(",")
	if len(fs)>2:
		st.append(fs)
st=st[1:]
st=st[:-1]
cn=cdb.Db().connection()
cur=cn.cursor()
cur.execute("delete from drug where 1;")
cur.execute("delete from stock where 1;")
for s in st:
	drug=s[1]
	d=s[4]
	exp=dt.datetime.strptime(d,"%b-%y").date()
	batch=s[3]
	rate=s[5]
	mrp=s[6]
	count=s[7]
	cur.execute("select * from drug where name like %s;",(drug))
	if cur.rowcount>0:
		r=cur.fetchone()
		drugid=r[0]
	else:
		cur.execute("insert into drug (name) values (%s);",(drug))
		drugid=cur.lastrowid
	cur.execute("insert into stock(drug_id,purchase_id,batch,start_count,cur_count,expiry,buy_price,price,tax,discount,terminate) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",(drugid,0,batch,count,count,exp,rate,mrp,0,0,0))
cn.commit()
