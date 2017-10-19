#!/usr/bin/env python
#from mttkinter.mtTkinter import *
from Tkinter import *
import bill,purchase,cancel,new,patient,showbills,password,editstock,review,creditnote,group
import printer as printbill
import shelve
import datetime as dt
import tkMessageBox
import connectdb as cdb
from bill import print_day_bills as print_daybills


class Pharma(Tk):

	def __init__(self):
		Tk.__init__(self)
		self.checkdb()
		self.config(width=600,height=400)
		self.title("Mukunda Pharmacy")
		self.addmenus()
		self.addshortcuts()
		self.stock=[]
		self.restock()
		f=Frame(self)
		bill.Bill(self,f).pack()
		f.pack()
		self.addstatus()
		self.mainloop()

	def addshortcuts(self):
		f=Frame(self,bd=1,relief=SUNKEN)
		f.pack()
		photo=PhotoImage(file="./images/bill.png")
		b=Button(f,image=photo,text="bill",compound=BOTTOM,width=100,height=100,command=lambda x=self:bill.Bill(x))
		b.pack(side=LEFT)
		b.image=photo
		photo=PhotoImage(file="./images/purchase.png")
		b=Button(f,image=photo,text="purchase",compound=BOTTOM,width=100,height=100,command=lambda x=self:purchase.addStock(x))
		b.pack(side=LEFT)
		b.image=photo
		photo=PhotoImage(file="./images/return.png")
		b=Button(f,image=photo,text="cancel",compound=BOTTOM,width=100,height=100,command=lambda x=self:cancel.Cancel(x))
		b.pack(side=LEFT)
		b.image=photo
		photo=PhotoImage(file="./images/new.png")
		b=Button(f,image=photo,text="new",compound=BOTTOM,width=100,height=100,command=lambda :new.adder())
		b.pack(side=LEFT)
		b.image=photo
		photo=PhotoImage(file="./images/patient.png")
		b=Button(f,image=photo,text="patient",compound=BOTTOM,width=100,height=100,command=lambda:patient.Patient())
		b.pack(side=LEFT)
		b.image=photo
			
	def addmenus(self):
		menu=Menu(self)

		self.debug=BooleanVar()
		self.debug.set(False)
		sh=shelve.open("data.db")
		try:
			noprinter=sh['noprinter']
		except:
			noprinter=False
		self.debug.set(noprinter)
		
		repmenu=Menu(menu,tearoff=0)
		repmenu.add_command(label="Day Report",command=self.dayreport)
		repmenu.add_command(label="Last Month Report",command=self.monthreport)
		repmenu.add_command(label="Print day bills (yesterday)",command=self.print_day_bills)
		menu.add_cascade(label="Report",menu=repmenu)

		viewmenu=Menu(menu,tearoff=0)
		viewmenu.add_command(label="bills",command=lambda:showbills.ShowFiles())
		viewmenu.add_command(label="print stockists list", command=self.liststockists)
		viewmenu.add_command(label="review bills",command=self.reviewbills)
		viewmenu.add_command(label="enter credit note",command=lambda:creditnote.CreditNote())
		viewmenu.add_command(label="group drugs",command=lambda:group.Group())
		menu.add_cascade(label="View",menu=viewmenu)

		adminmenu=Menu(menu,tearoff=0)
		adminmenu.add_command(label="Pay Stockists",command=self.purchasepay)
		adminmenu.add_command(label="Passwords",command=lambda:password.Password())
		adminmenu.add_command(label="Edit Stock",command=self.editstock)
		adminmenu.add_checkbutton(label="Debug",command=self.noprinter,variable=self.debug)
		adminmenu.add_command(label="Set Printers",command=self.setprinters)
		adminmenu.add_command(label="Set Db params",command=self.dbparams)
		adminmenu.add_command(label="Set GST rates",command=self.setgst)
		menu.add_cascade(label="Admin",menu=adminmenu)

		self.config(menu=menu)
		
	def addstatus(self):
		f=Frame(self,border=3,relief=RIDGE)
		f.pack(side=BOTTOM,expand=1,fill=X)
		self.statusSale=IntVar()
		self.statusSale.set(0)
		self.statusIp=IntVar()
		self.statusIp.set(0)
		Label(f,text="Sale : ").pack(side=LEFT,padx=20)
		Label(f,textvariable=self.statusSale).pack(side=LEFT)
		Label(f,text="IP sale = ").pack(side=LEFT,padx=20)
		Label(f,textvariable=self.statusIp).pack(side=LEFT)
		self.restatus()
	
	def restatus(self):
		sh=shelve.open("data.db")
		ipsale=sh["ipsale"]
		sale=sh["sale"]
		self.statusSale.set(int(sale))
		self.statusIp.set(int(ipsale))
		sh.close()
		
	def editstock(self):
		if not password.askpass():
			return
		editstock.EditStock()

	def dayreport(self):
		if not password.askpass():
			tkMessageBox.showerror("wrong password","try again")
			return
		sh=shelve.open("data.db")
		lines=["     DAY REPORT","     "+str(dt.date.today())]
		try:
			lastbill=sh['lastbill']
		except:
			lastbill=0
		try:
			lastprint=sh['lastprint']
		except:
			lastprint=0
		try:
			myar=sh['bills']
		except:
			myar=sh['bills']={"sale":[],"ipsale":[]}
		lines.append("report from bill#"+str(lastprint+1)+ " to #"+str(lastbill))
		lines.append("")
		lines.append('sale     :'+"{0:.2f}".format(sh['sale']))
		lines.append('ip sale  :'+"{0:.2f}".format(sh['ipsale']))
		lines.append('self sale:'+"{0:.2f}".format(sh['selfsale']))
		lines.append('return   :'+"{0:.2f}".format(sh['return']))
		lines.append('discharge:'+"{0:.2f}".format(sh['discharge']))
		lines.append('purchase :'+"{0:.2f}".format(sh['purchase']))
		lines.append("")
		for l in myar['sale'] :
			lines.append(" {:7d} - {:8.2f}".format(l[0],l[1]))
		printbill.printinfo(lines)
		sh['sale']=0
		sh['purchase']=0
		sh['return']=0
		sh['ipsale']=0
		sh['selfsale']=0
		sh['discharge']=0
		sh['lastprint']=lastbill
		self.statusSale.set(sh['sale'])
		self.statusIp.set(sh['ipsale'])
		myar={"sale":[],"ipsale":[]}
		sh['bills']=myar
		sh.close()
		self.restatus()
	
	def monthreport(self):
		if not password.askpass("admin"):
			tkMessageBox.showerror("error","wrong password")
			return
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="select min(id), max(id) from bill where year(date)=year(current_date-interval 1 month) and month(date)=month(current_date-interval 1 month);"
		cur.execute(sql)
		row=cur.fetchone()
		(firstid,lastid)=(row[0],row[1])		
		sql="select date, sum(net) from bill where year(date)=year(current_date-interval 1 month) and month(date)=month(current_date-interval 1 month) group by date;"
		cur.execute(sql)
		rows=cur.fetchall()
		lines=[]
		today=dt.date.today()
		first=today.replace(day=1)
		lastmonth=first-dt.timedelta(days=1)
		mony=lastmonth.strftime("%Y %B")
		lines.append("Sale Report "+mony)
		lines.append(" ")
		lines.append("from bill #"+str(firstid)+ " to #"+str(lastid)) 
		lines.append(" ")		
		for r in rows:
			item= ' {}   {:10.2f}'.format(r[0],r[1])
			lines.append(item)
		printbill.printinfo(lines)	
		
	def purchasepay(self):
		if not password.askpass("admin"):
			tkMessageBox.showerror("wrong password","try again")
			return 
		con=cdb.Db().connection()
		cur=con.cursor()
		sql = "select * from stockist order by name;"
		cur.execute(sql)
		stockists=cur.fetchall()
		items =["   PURCHASE PAYMENT"," "]
		for stockist in stockists:
			sql="select count(amount), sum(amount) ,group_concat(amount) from purchase where date < date_format(now(),'%Y-%m-01') and paid!=1 and stockist="+str(stockist[0])+";"
			print sql
			cur.execute(sql)
			if cur.rowcount>0:
				res=cur.fetchone()			
				count=res[0]
				amount=res[1]
				bills=res[2]
				if count>0:
					item= " {:30s}{:10.2f} ::{}".format(stockist[1]+" ("+str(count)+")",amount,bills)
					items.append(item)
					sql="update purchase set paid=1 where stockist="+str(stockist[0])+" and date<date_format(now(),'%Y-%m-01');"
					cur.execute(sql)
		con.commit()
		printbill.printinfo(items)
	
	def liststockists(self):
		if not password.askpass("admin"):
			tkMessageBox.showerror("error","wrong password")
			return
		sql = "select name from stockist order by name;"
		lines=["STOCKISTS"," "]
		con=cdb.Db().connection()
		cur=con.cursor()
		cur.execute(sql)
		result=cur.fetchall()
		for r in result:
			lines.append(r[0])
		printbill.printinfo(lines)
	
	def reviewbills(self):
		if password.askpass("admin"):
			review.Review(status="admin")
		else:
			review.Review()

	def noprinter(self):
		if not password.askpass("admin"):
			return
		sh=shelve.open("data.db")
		sh['noprinter']=self.debug.get()
				
	def setprinters(self):
		printbill.Checkprinters()
	
	def dbparams(self):
		if password.askpass("admin"):
			win=cdb.DbVariables()
			
	def setgst(self):
		if password.askpass("admin"):
			SetTax(Toplevel())
	
	def checkdb(self):
		try:
			db=cdb.Db()
			d=db.connection()
		except:
			a=cdb.DbVariables()
			a.wait_window()
	
	def print_day_bills(self):
		if not password.askpass():
			return
		d=dt.date.today()-dt.timedelta(days=1)
		print_daybills(d)
		
	def restock(self):
		db=cdb.Db().connection()
		cursor=db.cursor()
		sql="select drug.name as drug, sum(stock.cur_count) as count, min(stock.expiry) as expiry, max(stock.price) as price ,saletable.last_month_sale "\
			"from drug join stock on drug.id=stock.drug_id left join "\
			"(select sum(sale.count) as last_month_sale, stock.drug_id as drugid from sale join stock on sale.stock=stock.id join bill "\
			"on sale.bill=bill.id where bill.date>curdate() - interval 30 day group by drugid)saletable on drug.id=saletable.drugid "\
			"where stock.expiry>curdate()+ interval 20 day and stock.cur_count>0  group by drug.id order by drug.name;"
		cursor.execute(sql)
		rows=cursor.fetchall()
		stock=[]
		for row in rows:
			stock.append(row)
		self.stock=stock
		self.event_generate("<<stock_changed>>")
		
class SetTax (Frame):

	def __init__(self,parent=None):
		if not parent:
			parent=Tk()
		Frame.__init__(self,parent)
		sh=shelve.open('data.db')
		try:
			cgst=sh['cgst']
			sgst=sh['sgst']
		except:
			cgst=0
			sgst=0
		self.pack()
		self.varCgst=StringVar()
		self.varCgst.set(cgst)
		self.varSgst=StringVar()
		self.varSgst.set(sgst)
		Label(self,text="CGST").grid(row=0,column=0)
		Entry(self,textvariable=self.varCgst).grid(row=0,column=1)
		Label(self,text="SGST").grid(row=1,column=0)
		Entry(self,textvariable=self.varSgst).grid(row=1,column=1)
		Button(self,text="Save",command=self.save).grid(row=2,column=1)
		
	def save(self):
		sh=shelve.open('data.db')
		sh['cgst']=self.varCgst.get()
		sh['sgst']=self.varSgst.get()
		self.master.destroy()
		

if __name__=="__main__":
	Pharma()
