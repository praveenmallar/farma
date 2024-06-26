from tkinter import *
import connectdb as cdb
import comp
import calpicker
import tkinter.messagebox as tkMessageBox
import printer as printbill
import shelve
import datetime as dt

class addStock(Frame):

	def __init__(self,master=None, parent=None,*args, **kwargs):
		if not parent:
			parent=Toplevel(master)
		Frame.__init__(self,parent,*args,**kwargs)
		self.config(bg="#cccccc")
		self.parent=parent
		self.master=master
		self.items=[]
		parent.title("Purchase")
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
		
		ftop=Frame(self,bd=1,relief=RAISED,background="#cccccc")
		ftop.pack(side=TOP,fill=X,expand=1)
		myfont=("Times",10,"bold")

		#frame1 - to select bill details
		f1=Frame(ftop,bd=1,relief=GROOVE,bg="#dddddd")
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
		f2=Frame(ftop,bg="#dddddc")
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
		self.cgstp=DoubleVar()
		comp.NumEntry(f2,textvariable=self.cgstp,width=3).pack(side=LEFT)
		self.cgstp.set(0)
		Label(f2,text="SGST",font=myfont).pack(side=LEFT)
		self.sgstp=DoubleVar()
		comp.NumEntry(f2,textvariable=self.sgstp,width=3).pack(side=LEFT)
		self.sgstp.set(0)
		Label(f2,text="Expiry",font=myfont).pack(side=LEFT)
		self.expiry=calpicker.Calbutton(f2,width=14)
		self.expiry.pack(side=LEFT)
		self.add=Button(f2,text="Add",command=self.addstock,font=myfont)
		self.add.bind("<Return>",self.addstock)
		self.add.pack(side=LEFT)
		f2.pack(side=TOP)

		#frame3 - bill list
		f=Frame(self,width=850,height=300,bg="#e1e1ef")
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
			f.cgst=self.cgstp.get()
			f.sgst=self.sgstp.get()
			if not f.cgst== f.sgst:
				raise ValueError("cgst not equal to sgst")
		except ValueError:
			tkMessageBox.showerror("Error","error in GST",parent=self.parent)
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
		self.cgstp.set(0)
		self.sgstp.set(0)
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
	
		
		
	def addbill(self,event=None):
		if not  tkMessageBox.askyesno("Confirm","Save the purchase?",parent=self.parent):
			return 
		db=cdb.Db().connection()
		cur = db.cursor()

		stockist=self.stockists.get()
		billno=self.billno.get()
		date=self.date.get()
		total=str(self.total.get())
		bill_cgst=str(self.cgst.get())
		bill_sgst=str(self.sgst.get())
		gstbill=self.gstbill.get()
		
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
			printout.append("{0:10s}{1:4s}{2:8s}{3:8s}{4:4s}{5:6s}{6:3s}".format("drug","ct","rate","mrp","gst","exp","sl"))
			for f in self.items:
				drug=f.drug
				batch=f.batch
				count=f.count
				rate=f.rate
				if gstbill==1:
					mrp=f.mrp/(1+f.cgst/100+f.sgst/100)
				else:
					mrp=f.mrp
				disc=f.disc
				expiry=f.expiry
				dsql="select id from drug where name='"+drug+"';"
				cur.execute(dsql)
				row=cur.fetchone()
				drugid=row[0]
				sql="select sum(stock.cur_count) from stock where stock.drug_id={} and stock.expiry> curdate();"
				cur.execute(sql.format(drugid))
				r=cur.fetchone()
				existing_stock=r[0]
				sql="select sum(sale.count) from sale join bill on sale.bill=bill.id join stock on sale.stock=stock.id where bill.date> date_add(curdate(), interval -1 month) and stock.drug_id={};".format(drugid)
				cur.execute(sql)
				r=cur.fetchone()
				lastmonth_sale=r[0]
				if gstbill==1:
					sql="insert into stock (batch,expiry,start_count,cur_count,drug_id,price,cgstp,sgstp, purchase_id,buy_price, discount,terminate,tax) 						values ('{}',str_to_date('{}','{}'),{},{},{},{},{},{},{},{},{},0,0)".format(batch,expiry,'%d-%b-%y',count,count,drugid,mrp,f.cgst,f.sgst,billid,rate,disc)
					print(sql)
					cur.execute(sql)
				else:
					sql="insert into stock (batch,expiry,start_count,cur_count,drug_id,price, purchase_id,buy_price, discount,terminate) values  ('{}',str_to_date('{}','{}'),{},{},{},{},{},{},{},{},{},0)".format(batch,expiry,'%d-%b-%y',count,count,drugid,mrp,billid,rate,disc)
					print(sql)
					cur.execute(sql)
				billtotal=billtotal+count*rate
				if gstbill==1:
					mrp=f.mrp
				printout.append("{0:10.10s}-{1:4d}-{2:6.2f}-{3:6.2f}-{4:2.2s}-{5:%y%m}-{6:2.1f}".format(drug,int(count),float(rate),float(mrp),str(int(f.cgst)), dt.datetime.strptime(expiry,"%d-%b-%y").date(),float(lastmonth_sale or 0)/float(existing_stock or 1) ))
			db.commit()
			printout.append(" ")
			printout.extend(["net total: "+str(billtotal),"bill total: "+total,"",""])
			printbill.printinfo(printout)
			sh=shelve.open("data")
			try:
				curpurchase=float(sh['purchase'])
			except:
				curpurchase=0
			sh['purchase']=curpurchase+float(total)
			sh.close()
			self.items=[]
			self.refreshcanvas()
			self.master.restock()
			self.drug.focus()

		except cdb.mdb.Error as e:
			tkMessageBox.showerror("Error in database:", "error {}: {}" .format(e.args[0],e.args[1]),parent=self.parent)
			if db:
				db.rollback()
		finally :
			db.close()


if __name__=="__main__":
	root=addStock()
	root.mainloop()
	
		
