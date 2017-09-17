from Tkinter import *
import connectdb as cdb
import comp
import calpicker
import printer as printbill 
import datetime as dt
import tkMessageBox
import patient 
import shelve

class drugComp(Frame):
	def __init__(self, parent=None,listitems=[["mango",1],["pineapple",2]],listheight=4,  **kwargs):
		Frame.__init__(self,parent)	
		self.c1=comp.myComp2(self,listitems,listheight,**kwargs)
		self.l1=Label(self,width=5)
		self.l2=Label(self,width=8)
		self.c1.pack(side=LEFT)
		self.l1.pack(pady=10)
		self.l2.pack()
		self.pack()
		self.c1.bind("<<listChanged>>",self.textchanged)
		
	def textchanged(self,a=None,b=None,c=None):
		text=self.c1.get()
		if text:		
			self.l1.config(text=text[1])
		if text[4]!=None and ((text[1]<text[4]/5) or int(text[1]<2)):
			self.l1.config(fg="red")
			self.l2.config(text=str(text[4]))
		else:
			self.l1.config(fg="black")
			self.l2.config(text="")
	def get(self):
		ret=self.c1.get()
		if ret: return ret
		else: return None
	def clear(self):
		self.c1.clear()
	def focus(self):
		self.c1.focus()	

def sell_rate(mrp,discount):
	return mrp-float(mrp)*float(discount)/100
def sell_discount(mrp,discount):
	return float(mrp)*(float(discount)/100)

class Bill(Frame):
	def __init__(self,master,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.rw=master
		try:
			self.master.title("Make Bill")	
		except:
			pass	
		self.config(padx=20,pady=10,bd=2,relief=RIDGE,bg="#ffffee")	
		self.items=[]
		self.patients=patient.getPatients()
		temp=[[" ",None]]
		for pat in self.patients:
			temp.append([pat[1]+" :"+pat[0],pat[2]])
		self.patients=temp
		db=cdb.Db().connection()
		cursor=db.cursor()
		cursor.execute("select * from doc order by name;")
		result=cursor.fetchall()
		docs=[]
		for row in result:
			docs.append(row[1])
		self.drugs=[]


		f1=Frame(self,bd=1,relief=GROOVE)
		f1.pack(side=TOP,pady=5)
		myfont=("Times",10,"bold")
		Label(f1,text="Patient",font=myfont).grid(row=0,column=0,sticky=E,padx=4,pady=2)
		self.varPatient=StringVar()
		Entry(f1,textvariable=self.varPatient).grid(row=0,column=1,sticky=E+W,padx=4,pady=2)
		Label(f1,text="select Doctor",font=myfont).grid(row=1,column=0,sticky=E,padx=4,pady=2)
		self.doc=comp.myComp(f1,listitems=docs,listheight=2,width=14)
		self.doc.grid(row=1,column=1,sticky=E+W+N+S,padx=4,pady=2)

		self.f2=f2=Frame(self)
		f2.pack(side=TOP,pady=10)
		self.populateDrugFrame(f2,myfont)
		self.rw.master.bind("<<stock_changed>>",lambda x=None:self.populateDrugFrame(self.f2,myfont))
		
		f=Frame(self)		
		f.pack(side=LEFT,fill=X,expand=1,padx=10,pady=10)
		sb=Scrollbar(f)
		sb.pack(side=RIGHT,fill=Y)
		f3=self.f3=Canvas(f,bd=1,relief=SUNKEN,yscrollcommand=sb.set,width=300,height=300)
		f3.pack(fill=BOTH,expand=1) 
		sb.config(command=f3.yview)

		f4=Frame(self)
		f4.pack(side=RIGHT,fill=X,expand=1)
		self.selfbill=IntVar()
		Checkbutton(f4,text="Self Bill",variable=self.selfbill,background="cyan",bd=1,relief="sunken").pack(side=TOP,pady=15,fill=BOTH)
		Label(f4,text="IP Patient").pack(side=TOP)
		self.patient=comp.myComp2(f4,self.patients,listheight=6)	
		self.patient.pack(side=TOP)	
		b=Button(f4,text="Submit\nBill", font=("Times",14,"bold"),padx=10,pady=10,command=self.addbill)
		b.bind("<Return>",self.addbill)		
		b.pack(side=BOTTOM)
		self.pack()

	def adddrug(self,event=None):
		drug=self.drugsComp.get()
		count=self.drug.get()
		if drug is not None:
			f=Frame(self.f3,bd=1, relief=RIDGE)
			f.drug=StringVar()
			f.drug.set(drug[0])
			f.drugcount=IntVar()
			f.drugcount.set(count)
			f.drugprice=drug[3]
			Label(f,textvariable=f.drug,width=15).pack(side=LEFT)
			Label(f,textvariable=f.drugcount,width=5).pack(side=LEFT)
			Button(f,text="remove",command=lambda:self.removeframe(f)).pack(side=LEFT)
			self.items.append(f)
			self.refreshcanvas()
		self.drugsComp.clear()
		self.drug.set("")
		self.drugsComp.focus()

	def refreshcanvas(self):
		self.f3.delete(ALL)	
		i=0
		total=0
		for f in self.items:
			self.f3.create_window(1,1+i*32,window=f, anchor=NW)
			i=i+1
			total+=(f.drugcount.get()*f.drugprice)
		self.f3.update_idletasks()
		self.f3.config(scrollregion=self.f3.bbox(ALL))
		self.cur_total.set(total)

	def removeframe(self,frame):
		self.items.remove(frame)
		self.refreshcanvas()
	
	def populateDrugFrame(self,frame,myfont=("Times",10,"bold")):
		print "populate", frame,myfont
		try:
			frame.f2.destroy()
		except Exception:
			pass
		f2=Frame(frame)
		f2.pack(ipadx=10,ipady=10,fill=BOTH)
		Label(f2,font=myfont,text="Drug").pack(side=LEFT)
		self.drugsComp=drugComp(f2,listitems=self.rw.stock,listheight=2,width=20)
		self.drugsComp.pack(side=LEFT)
		Label(f2,text="count",font=myfont).pack(side=LEFT)
		self.drug=StringVar()
		comp.NumEntry(f2,textvariable=self.drug, width=6).pack(side=LEFT)
		b=Button(f2,command=self.adddrug,text="Add",font=myfont)
		b.pack(side=LEFT)
		b.bind("<Return>",self.adddrug)
		f=Frame(f2,bd=1, relief=RIDGE)
		f.pack(side=LEFT)
		Label(f,text="total: ").pack()
		self.cur_total=StringVar()
		Label(f,textvariable=self.cur_total,width=10).pack()
		frame.f2=f2

	def addbill(self,event=None):
		db=cdb.Db().connection()
		cur = db.cursor()
		patient=self.varPatient.get()
		doc=None
		IP=None
		ip=None
		billid=0
		doc=self.doc.get().title()
		selfbill=self.selfbill.get()
		if selfbill==0:
			ip=self.patient.get()
			if ip: 
				patient=ip[0].split(" :")[0]
				IP=ip[0].split(" :")[1]
				patientid=ip[1]
		date=dt.date.today()
		
		try:
			docid=None
			if doc:			
				sql="select id from doc where name='"+doc+"'"
				cur.execute(sql)
				row=cur.fetchone()
				docid=row[0]
			
			if selfbill==0:
				sql="insert into bill(name, doc, date) values(%s,%s,%s);"
				cur.execute(sql,(patient,docid,date.isoformat()) )
				billid=cur.lastrowid
			billtotal=0.0
			discount=0
			cgst=0.0
			sgst=0.0
			items=[]

			for frame in self.items:
				drug=frame.drug.get()
				count=frame.drugcount.get()
				i=0
				cur.execute("select id from drug where name =%s",[drug])
				row=cur.fetchone()
				drugid=row[0]
				dictcur=db.cursor(cdb.dictcursor)
				dictcur.execute("select id, cur_count,price,cgst,sgst,tax,discount,batch,expiry from stock where expiry > curdate() and drug_id=%s and cur_count>0 order by expiry",[drugid])
				batches=dictcur.fetchall()
				for batch in batches:
					if batch['cgst']:
						batch_cgst=float(batch['cgst'])
					else:
						batch_cgst=0
					if batch['sgst']:
						batch_sgst=float(batch['sgst'])
					else:
						batch_sgst=0	
					if count>batch["cur_count"]:
						count=count-batch["cur_count"]
						cur.execute("update stock set cur_count=0 where id=%s;",[batch["id"]])
						if selfbill==0:
							cur.execute("insert into sale(stock,bill,count) values(%s,%s,%s);", (batch["id"],billid,batch["cur_count"]))
						saleamount=batch["cur_count"]*sell_rate(batch['price'],batch['discount'],batch['tax'])
						billtotal=billtotal+saleamount
						cgst=cgst+batch_cgst*batch['cur_count']
						sgst=sgst+batch_sgst*batch['cur_count']
						discount+=discount+batch['cur_count']*sell_discount(batch['price'],batch['discount'])
						items.append([drug+"("+str(batch['cur_count'])+')-'+str(batch['batch']),saleamount,batch['expiry']])  
					elif count>0:
						newcount=batch["cur_count"]-count
						cur.execute("update stock set cur_count=%s where id=%s;",(newcount,batch["id"]))
						if selfbill==0:
							cur.execute("insert into sale(stock,bill,count) values(%s,%s,%s);",(batch["id"],billid,count))
						saleamount=count*sell_rate(batch['price'],batch['discount'],batch['tax'])
						billtotal=billtotal+saleamount
						cgst=cgst+count*batch_cgst
						sgst=sgst+count*batch_sgst
						discount+=count*sell_discount(batch['price'],batch['discount'])
						items.append([drug+"("+str(count)+')-'+str(batch['batch']),saleamount,batch['expiry']])  
						count=0
					else:
						break						
				if count > 0:
					raise cdb.mdb.Error(420, "not enough stock of " +drug )
			
			if selfbill==0:
				cur.execute("update bill set cgst=%s where id=%s;",(cgst,billid))
				cur.execute("update bill set sgst=%s where id=%s;",(sgst,billid))
				cur.execute("update bill set net=%s where id=%s;",(billtotal+cgst+sgst,billid))	
			if ip:		
				cur.execute("insert into credit(patientid,billid) values(%s,%s);",(patientid,billid))
			db.commit()
			printbill.printbill(billid,patient,doc,date,billtotal,cgst,sgst,items,discount,IP,selfbill)
			sh=shelve.open("data.db")
			if selfbill==0:			
				if ip:
					token="ipsale"
				else:
					token="sale"
				sh['lastbill']=billid
			else:
				token="selfsale"
			try:
				cursale=sh[token]
			except:
				cursale=0
			sh[token]=float(cursale)+float(billtotal+cgst+sgst)
			self.items=[]
			self.refreshcanvas()
			self.varPatient.set("")
			self.doc.clear()
			self.patient.clear()
			self.selfbill.set(0)
			self.rw.restock()
		except cdb.mdb.Error as e:
			tkMessageBox.showerror("Error","error %d: %s" %(e.args[0],e.args[1]),parent=self.master)
			if db:
				db.rollback()
		finally :
			db.close()

def print_day_bills(day):
	cur=cdb.Db().connection().cursor(cdb.dictcursor)
	cur.execute("select bill.id as id,bill.name as name,doc.name as doc,date,net from bill join doc on doc.id=bill.doc where date=%s",(day.isoformat()))
	rows=cur.fetchall()
	for bill in rows:
		id=bill['id']
		cur.execute("select drug.name as drug,sale.count,stock.batch,stock.price,stock.discount,stock.tax,stock.expiry from sale join stock on sale.stock=stock.id"\
				" join drug on stock.drug_id=drug.id where sale.bill=%s",(id))
		r=cur.fetchall()
		items=[]
		for sale in r:
			amount=sale['count']*sell_rate(sale['price'],sale['discount'],sale['tax'])
			f1=sale['drug']+"("+str(sale['count'])+")"+str(sale['batch'])	
			items.append([f1,amount,sale['expiry']	])	
		printbill.printbill(bill['id'],bill['name'],bill['doc'],bill['date'],bill['net'],items)
		

	
if __name__=="__main__":
	
	Bill().mainloop()

