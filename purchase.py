from Tkinter import *
import connectdb as cdb
import comp
import calpicker
import tkMessageBox
import printer as printbill
import shelve
import datetime as dt
from bill import sell_rate

class addStock(Frame):

	def __init__(self, parent=None,*args, **kwargs):
		if not parent:
			parent=Tk()
		Frame.__init__(self,parent,*args,**kwargs)
		self.items=[]
		db=cdb.Db().connection()
		cursor = db.cursor()
		cursor.execute("select * from stockist")
		result=cursor.fetchall()
		stockists=[]
		for row in result:
			stockists.append(row[1])
		drugs=[]
		cursor.execute("select * from drug")
		result=cursor.fetchall()
		for row in result:
			drugs.append(row[1])
		
		ftop=Frame(self,bd=1,relief=RAISED,background="cyan")
		ftop.pack(side=TOP,fill=X,expand=1)
		myfont=("Times",10,"bold")

		#frame1 - to select bill details
		f1=Frame(ftop,bd=1,relief=GROOVE)
		Label(f1,text="Stockist",font=myfont).grid(row=0,column=0,sticky=E,padx=4,pady=2)
		self.stockists=comp.myComp(f1,listitems=stockists,listheight=2,width=14)
		self.stockists.grid(row=0,column=1,sticky=E+W+N+S,padx=4,pady=2)
		Label(f1,text="Bill Number",font=myfont).grid(row=1,column=0,sticky=E,padx=4,pady=2)
		self.billno=Entry(f1,width=14)
		self.billno.grid(row=1,column=1,sticky=E+W+N+S,padx=4,pady=2)
		Label(f1,text="Date",font=myfont).grid(row=2,column=0,sticky=E,padx=4,pady=2)
		self.date=calpicker.Calbutton(f1,width=14)
		self.date.grid(row=2,column=1,sticky=E+W+N+S,padx=4,pady=2)
		Label(f1,text='CGST',font=myfont).grid(row=3,column=0,sticky=E,padx=4,pady=2)
		self.cgst=comp.NumEntry(f1,width=14)
		self.cgst.grid(row=3,column=1,sticky=E+W+N+S,padx=4,pady=4)
		Label(f1,text='SGST',font=myfont).grid(row=4,column=0,sticky=E,padx=4,pady=2)
		self.sgst=comp.NumEntry(f1,width=14)
		self.sgst.grid(row=4,column=1,sticky=E+W+N+S,padx=4,pady=4)
		Label(f1,text="Total",font=myfont).grid(row=5,column=0,sticky=E,padx=4,pady=2)
		self.total=comp.NumEntry(f1,width=14)
		self.total.grid(row=5,column=1,sticky=E+W+N+S,padx=4,pady=4)
		f1.pack(side=TOP)	

		#frame2 - to add stocks
		f2=Frame(ftop)
		Label(f2,text="Drug",font=myfont).pack(side=LEFT)
		self.drug=comp.myComp(f2,listitems=drugs,listheight=3,width=14)
		self.drug.pack(side=LEFT)
		Label(f2,text="Batch",font=myfont).pack(side=LEFT)
		self.batch=Entry(f2,width=10)
		self.batch.pack(side=LEFT)
		Label(f2,text="Count",font=myfont).pack(side=LEFT)
		self.count=comp.NumEntry(f2,width=5)
		self.count.pack(side=LEFT)
		Label(f2,text="Rate",font=myfont).pack(side=LEFT)
		self.rate=comp.NumEntry(f2,width=10)
		self.rate.pack(side=LEFT)
		Label(f2,text="MRP",font=myfont).pack(side=LEFT)
		self.mrp=comp.NumEntry(f2,width=10)
		self.mrp.pack(side=LEFT)
		Label(f2,text="Discount",font=myfont).pack(side=LEFT)
		self.disc=DoubleVar()
		comp.NumEntry(f2,width=10,textvariable=self.disc).pack(side=LEFT)
		self.disc.set(0)
		Label(f2,text="CGST",font=myfont).pack(side=LEFT)
		self.cgst=DoubleVar()
		comp.NumEntry(f2,textvariable=self.cgst,width=3).pack(side=LEFT)
		self.cgst.set(0)
		Label(f2,text="SGST",font=myfont).pack(side=LEFT)
		self.sgst=DoubleVar()
		comp.NumEntry(f2,textvariable=self.sgst,width=3).pack(side=LEFT)
		self.sgst.set(0)
		self.tax=DoubleVar()
		Label(f2,text="Expiry",font=myfont).pack(side=LEFT)
		self.expiry=calpicker.Calbutton(f2,width=14)
		self.expiry.pack(side=LEFT)
		self.add=Button(f2,text="Add",command=self.addstock,font=myfont)
		self.add.bind("<Return>",self.addstock)
		self.add.pack(side=LEFT)
		f2.pack(side=TOP)

		#frame3 - bill list
		f=Frame(self,width=850,height=300)		
		f.pack(side=LEFT,fill=X,expand=1)
		sb=Scrollbar(f)
		sb.pack(side=RIGHT,fill=Y)
		f3=self.f3=Canvas(f,bd=1,relief=SUNKEN,yscrollcommand=sb.set,width=800,height=300)
		f3.pack(fill=BOTH,expand=1)
		sb.config(command=f3.yview)
		self.gstbill=IntVar()
		Checkbutton(self,text="GST Bill",variable=self.gstbill,onvalue=1,offvalue=0).pack(pady=50)
		self.gstbill.set(1)
		submitButton=Button(self,text="Submit\nBill", font=("Times",14,"bold"),padx=10,pady=10,command=self.addbill)
		submitButton.bind("<Return>",self.addbill)		
		submitButton.pack()

		self.pack()
		self.stockists.focus()

	def addstock(self,event=None):
		f=Frame(self.f3,bd=1,relief=RIDGE)
		try:
			f.cgst=self.cgst.get()
			f.sgst=self.sgst.get()
			if f.cgst==0 or f.sgst==0:
				raise ValueError("cgst or sgst cant be 0")
		except ValueError:
			tkMessageBox.showerror("Error","error in GST")
			return			
		f.drug=self.drug.get()
		Label(f,width=20,height=1,text=f.drug).pack(side=LEFT)
		f.batch=self.batch.get()		
		Label(f,width=14,height=1,text="batch "+f.batch).pack(side=LEFT)
		f.count=int(self.count.get())
		Label(f,width=10,height=1,text="count "+str(f.count)).pack(side=LEFT)
		f.rate=float(self.rate.get())
		Label(f,width=12,height=1,text="rate "+str(f.rate)).pack(side=LEFT)
		f.mrp=float(self.mrp.get())
		Label(f,width=12,height=1,text="mrp "+str(f.mrp)).pack(side=LEFT)
		f.disc=float(self.disc.get())
		Label(f,width=8,height=1,text="disc "+str(f.disc)).pack(side=LEFT)
		Label(f,width=8,height=1,text="cgst "+str(f.cgst)).pack(side=LEFT)
		Label(f,width=8,height=1,text="sgst "+str(f.sgst)).pack(side=LEFT)
		f.expiry=self.expiry.get()
		Label(f,width=12,height=1,text="exp "+str(f.expiry)).pack(side=LEFT)
		b=Button(f,text="remove",width=10)
		b.config(command=lambda: self.removeframe(b))		
		b.pack(side=LEFT)	
		self.items.append(f)
		self.refreshcanvas()
		self.drug.clear()
		self.batch.delete(0,END)
		self.count.delete(0,END)
		self.rate.delete(0,END)
		self.mrp.delete(0,END)
		self.disc.set(0)
		self.tax.set(0)
		self.drug.focus()

	def refreshcanvas(self):
		self.f3.delete(ALL)
		i=0
		for f in self.items:
			self.f3.create_window(1,1+i*32,window=f, anchor=NW)
			i=i+1
		self.f3.update_idletasks()
		self.f3.config(scrollregion=self.f3.bbox(ALL))

	def removeframe(self,button):
		self.items.remove(button.master)
		self.refreshcanvas()
	
	def getgst(self,mrp):
		print mrp
		sh=shelve.open("data.db")
		try:
			cgst=float(sh["cgst"])
		except:
			cgst=0
		try:
			sgst=float(sh["sgst"])
		except:
			sgst=0
		cgst=mrp*cgst/100
		sgst=mrp*sgst/100
		sell_rate=mrp-(cgst+sgst)
		print sell_rate
		return (sell_rate,cgst,sgst)
		
		
	def addbill(self,event=None):
		db=cdb.Db().connection()
		cur = db.cursor()

		stockist=self.stockists.get()
		billno=self.billno.get()
		date=self.date.get()
		total=str(self.total.get())
		bill_cgst=str(self.cgst.get())
		bill_sgst=str(self.sgst.get())
		
		try:
			sql="select id from stockist where name='"+stockist+"';"
			cur.execute(sql)
			row=cur.fetchone()
			stockistid=row[0]
			sql="insert into purchase (bill,stockist,date,amount,cgst,sgst) values ('"+str(billno)+"','"+str(stockistid)+"',str_to_date('"+date+"','%d-%b-%y'),"+total+","+bill_cgst+","+bill_sgst+");"
			cur.execute(sql)
			billid=cur.lastrowid
			billtotal=0
			printout=["","","PURCHASE","",stockist,"bill: "+billno,""]
			printout.append("{0:12s}{1:4s}{2:8s}{3:8s}{4:6s}{5:4s}{6:5}".format("drug","ct","rate","mrp","exp","stk","sl"))
			for f in self.items:
				drug=f.drug
				batch=f.batch
				count=f.count
				rate=f.rate
				if self.gstbill.get()==1:
					mrp=self.getgst(f.mrp)
					print mrp
					sellrate=mrp[0]
					cgst=mrp[1]
					sgst=mrp[2]
					mrp=sellrate
					print mrp
				else:
					mrp=f.mrp
				print mrp
				disc=f.disc
				tax=f.tax
				expiry=f.expiry
				print expiry
				dsql="select id from drug where name='"+drug+"';"
				cur.execute(dsql)
				row=cur.fetchone()
				drugid=row[0]
				sql="select sum(stock.cur_count) from stock where stock.drug_id=%s and stock.expiry> curdate();"
				cur.execute(sql,[drugid])
				r=cur.fetchone()
				existing_stock=r[0]
				sql="select sum(sale.count) from sale join bill on sale.bill=bill.id join stock on sale.stock=stock.id where bill.date> date_add(curdate(), interval -1 month) and stock.drug_id=%s;"
				cur.execute(sql,[drugid])
				r=cur.fetchone()
				lastmonth_sale=r[0]
				if self.gstbill.get()==1:
					sql="insert into stock (batch,expiry,start_count,cur_count,drug_id,price,cgst,sgst, purchase_id,buy_price, tax,discount,terminate) 						values (%s,str_to_date(%s,%s),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0)"
					cur.execute(sql,(batch,expiry,'%d-%b-%y',count,count,drugid,mrp,cgst,sgst,billid,rate,tax,disc))
				else:
					sql="insert into stock (batch,expiry,start_count,cur_count,drug_id,price, purchase_id,buy_price, tax,discount,terminate) 						values (%s,str_to_date(%s,%s),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0)"
					cur.execute(sql,(batch,expiry,'%d-%b-%y',count,count,drugid,mrp,billid,rate,tax,disc))
					
				billtotal=billtotal+count*rate
				if self.gstbill.get()==1:
					mrp=mrp+cgst+sgst
				mrp=sell_rate(mrp,disc,tax)
				printout.append("{0:12.12s}-{1:4d}-{2:6.2f}-{3:6.2f}-{4:%b%y}-{5:3d}-{6:4d}".format(drug,int(count),float(rate),float(mrp), dt.datetime.strptime(expiry,"%d-%b-%y").date(),int(existing_stock or 0),int(lastmonth_sale or 0)))
			db.commit()
			printout.append(" ")
			printout.extend(["net total: "+str(billtotal),"bill total: "+total,"",""])
			printbill.printinfo(printout)
			sh=shelve.open("data.db")
			try:
				curpurchase=sh['purchase']
			except:
				curpurchase=0
			sh['purchase']=curpurchase+float(total)
			self.items=[]
			self.refreshcanvas()
			self.drug.focus()

		except cdb.mdb.Error,e:
			tkMessageBox.showerror("Error in database:", "error %d: %s" %(e.args[0],e.args[1]),parent=self.master)
			if db:
				db.rollback()
		finally :
			db.close()


if __name__=="__main__":
	root=addStock()
	root.mainloop()
	
		
