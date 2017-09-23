from Tkinter import *
import connectdb as cdb
import comp
import tkMessageBox
import printer as printbill
import shelve

class Cancel(Frame):
		
	def __init__(self,parent=None,*arg,**karg):
		if not parent:
			t=Toplevel()
			parent=t
		Frame.__init__(self,parent,*arg,**karg)
		self.pack()
		self.master.title("Cancel Bill")
		f1=Frame(self)  							#search frame		
		f1.pack(side=TOP,padx=15,pady=10,ipadx=20,ipady=10)
		Label(f1,text="Bill Number").pack(side=LEFT)
		self.billno=IntVar()
		self.billno.set("")
		t=comp.NumEntry(f1,textvariable=self.billno)
		t.pack(side=LEFT,padx=5)
		t.bind("<Return>",self.searchbill)
		b=Button(f1,text="Search",command=self.searchbill)
		b.pack(side=LEFT,padx=5)
		b.bind("<Return>",self.searchbill)

		f2=Frame(self)			#bill details
		f2.pack(side=TOP,fill=BOTH,expand=1,padx=10)
		sb=Scrollbar(f2)
		sb.pack(side=RIGHT,fill=Y)
		self.canvas=Canvas(f2,bd=1,relief=SUNKEN,yscrollcommand=sb.set,width=300,height=300)
		self.canvas.pack(fill=BOTH,expand=1)
		sb.config(command=self.canvas.yview)

		f3=Frame(self)
		f3.pack(side=TOP,ipadx=20,ipady=10)
		self.cancelbutton=Button(f3,text="cancel Bill",state=DISABLED,command=self.cancelbill)
		self.cancelbutton.pack(side=LEFT,padx=20,pady=10)
		self.updatebutton=Button(f3,text="update Bill",command=self.updatebill,state=DISABLED)
		self.updatebutton.pack(side=LEFT,padx=20,pady=10)
		self.reprintbutton=Button(f3,text="Reprint Bill",command=self.reprint,state=DISABLED)
		self.reprintbutton.pack(side=LEFT,pady=10)

	def searchbill(self,event=None):
		self.curbill=self.billno.get()
		self.canvas.delete(ALL)
		self.items=[]
		db=cdb.Db().connection()
		cur=db.cursor(cdb.dictcursor)
		sql="select drug.name,sale.id,sale.count,stock.price,stock.discount,stock.cgstp,stock.sgstp,bill.name as patient,bill.net as total,bill.date from bill join sale on bill.id=sale.bill join stock on sale.stock=stock.id join drug on stock.drug_id=drug.id where bill.id=%s;"
		cur.execute(sql,[str(self.curbill)])	
		rows=cur.fetchall()
		if len(rows)==0:
			return
		row=rows[0]
		f=Frame(self.canvas)
		Label(f,text=row['patient']).pack(side=LEFT,padx=10,pady=10)
		Label(f,text=row['date']).pack(side=LEFT,padx=10,pady=10)
		Label(f,text=row['total']).pack(side=LEFT,padx=10,pady=10)
		self.canvas.create_window(1,1,window=f,anchor=NW)	
		i=1	
		for row in rows:
			f=Frame(self.canvas)
			Label(f,text=row['name'],width=20).pack(side=LEFT,padx=10,pady=10)
			f.drug=row['name']
			f.oldcount=row['count']
			f.count=IntVar()
			f.count.set(f.oldcount)
			comp.NumEntry(f,textvariable=f.count,width=5).pack(side=LEFT,padx=10,pady=10)
			f.id=row['id']
			f.price=row['price'] (1+ row['cgstp']/100 + row['sgstp']/100)
			self.canvas.create_window(1,1+i*40,window=f,anchor=NW)
			i=i+1
			self.items.append(f)
		self.canvas.update_idletasks()
		self.canvas.config(scrollregion=self.canvas.bbox(ALL))
		self.cancelbutton.config(state=NORMAL)
		self.updatebutton.config(state=NORMAL)
		self.reprintbutton.configure(state=NORMAL)

	def updatebill(self):
		if not tkMessageBox.askyesno("confirm update","Are you sure you want to modify bill "+str(self.curbill),parent=self.master):
			return
		self.billno.set(self.curbill)
		con=cdb.Db().connection()
		cur=con.cursor()
		returnamount=0
		printout=[]
		printout.extend(printbill.header)
		printout.extend(("","    BILL RETURN ", "Bill number: "+str(self.curbill),""))
		ip=False
		if self.isip(self.curbill,cur):	
			ip=True
		try:
			for f in self.items:
				count=f.count.get()
				if count != f.oldcount:
					if count>=f.oldcount or self.isexpired(f.id,cur):
						printout.append("cant return "+ f.drug + " since either count entered is wrong, or the stock is expired")
						continue
					sql="update sale set count = %s where id=%s"
					cur.execute(sql,(str(count),str(f.id)))
					returnamount=returnamount+(f.oldcount-count)*f.price
					printout.append(f.drug+ "   "+ str(f.oldcount-count) + "     "+str((f.oldcount-count)*f.price) )
					sql= "update stock set cur_count=cur_count+%s where stock.id = (select stock from sale where id=%s);"
					cur.execute(sql,(str(f.oldcount-count),str(f.id)))

			if returnamount>0:
				sql= "update bill set net = net-%s where id=%s;"
				cur.execute(sql,(str(returnamount),str(self.curbill)))				
				printout.extend((""," RETURN AMOUNT:   "+str(returnamount)))
			con.commit()
			if not ip:
				printbill.printinfo(printout)
				self.reprint(cur)
				sh=shelve.open("data.db")
				try:
					billreturn=sh['return']
				except:
					billreturn=0
				sh['return']=float(billreturn)+float(returnamount)
			else:
				tkMessageBox.showinfo("Bill Updated", "bill print out only if not IP bill",parent=self.master)

		except cdb.mdb.Error as e:						
			tkMessageBox.showerror("Error "+str(e.args[0]),e.	args[1],parent=self.master)
			con.rollback()
		finally:
			con.close()
			self.searchbill()

	def cancelbill(self):
		if not tkMessageBox.askyesno("confirm Cancel","Are you sure you want to cancel bill "+str(self.curbill),parent=self.master):
			return
		self.billno.set(self.curbill)
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="select sale.id from sale join bill on sale.bill=bill.id join stock on sale.stock=stock.id where stock.expiry < curdate() + interval 30 day and bill.id= %s;"
		cur.execute(sql,[str(self.curbill)])
		if cur.rowcount>0:
			tkMessageBox.showerror("Can not cancel bill","looks like one of the item is near expiry",parent=self.master)
			return
		try:
			ip=False
			if self.isip(self.curbill,cur):	
				ip=True
			sql="select sale.id as saleid, sale.count as count,sale.stock as stock from sale where sale.bill=%s;"
			cur.execute(sql,[self.curbill])
			rows=cur.fetchall()
			for row in rows:
				sql="update stock set cur_count=cur_count+%s where stock.id=%s"
				cur.execute(sql,(row[1],row[2]))
				sql="update sale set count=0 where id=%s"
				cur.execute(sql,[row[0]])
			sql="select net from bill where id=%s;"
			cur.execute(sql,[self.curbill])
			row=cur.fetchone()
			returnamount=row[0]
			sql="update bill set net=0 where id=%s;"
			cur.execute(sql,[self.curbill])
			con.commit()
			if not ip:
				printout=[]
				printout.extend(printbill.header)
				printout.extend(("","    BILL CANCEL"))
				printout.extend(("Bill no:" + str(self.curbill),"","Refund amount  "+str(returnamount)))
				printbill.printinfo(printout)
				sh=shelve.open("data.db")
				try:
					billreturn=sh['return']
				except:
					billreturn=0
				sh['return']=float(billreturn)+float(returnamount)			
			else:
				tkMessageBox.showinfo("Bill Cancelled","Refund only if bill is not IP",parent=self.master)
			
		except cdb.mdb.Error as e:
			tkMessageBox.showerror("Error "+str(e.args[0]),e.	args[1],parent=self.master)
			con.rollback()
		finally:
			con.close()
			self.searchbill()

	def isexpired(self,sale,cur):
		sql="select stock.id from sale join stock on sale.stock=stock.id where stock.expiry>curdate()+interval 30 day and sale.id= %s;"
		cur.execute(sql,[sale])
		if cur.rowcount>0:
			return False
		else:
			return True
	
	def isip(self,bill,cur):
		sql="select patient.id from patient join credit on patient.id=credit.patientid join bill on credit.billid=bill.id where patient.discharged=0 and bill.id=%s;"
		cur.execute(sql,[bill])
		if cur.rowcount>0:
			return True
		else:
			return False
	
	def reprint(self,cur=None,biller=None):
		billno=self.curbill
		if not cur:
			cur=cdb.Db().connection().cursor()
		if not biller:
			sql="select bill.name, doc.name as doc,bill.date, bill.net, drug.name as drug, sale.count,stock.batch,stock.expiry,stock.price, stock.tax,stock.discount,bill.cgst,bill.sgst from bill join sale on sale.bill=bill.id join stock on sale.stock=stock.id join drug on stock.drug_id=drug.id left join doc on bill.doc=doc.id where bill.id=%s;"
			cur.execute(sql,[billno])
			r=cur.fetchone()
			patient=r[0]
			doc=r[1]
			date=r[2]
			total=r[3]-r[11]-r[12]
			cgst=r[11]
			sgst=r[12]
			cur.scroll(0,mode="absolute")
			rows=cur.fetchall()
			items=[]
			for r in rows:
				price=sell_rate(r[8],r[10],r[9])
				item=(r[4]+" ("+str(r[5])+") -"+str(r[6]),r[5]*price,r[7])
				items.append(item)
			sql="select patient.name from bill join credit on bill.id=credit.billid join patient on credit.patientid=patient.id where bill.id=%s and patient.discharged=0;"
			ip=None
			cur.execute(sql,[billno])
			if cur.rowcount>0:
				r=cur.fetchone()
				f=r[0].split("::")
				ip=f[0]
			biller={"billno":str(billno)+ "  COPY","patient":patient,"doc":doc,"date":date,"total":total,"items":items,"ip":ip,"cgst":cgst,"sgst":sgst}
		printbill.printbill(biller['billno'],biller['patient'],biller['doc'],biller['date'],biller['total'],biller['cgst'],biller['sgst'],biller['items'],biller['ip'])
		
if __name__=="__main__":
	f=Cancel()
	f.pack()
	f.mainloop()




