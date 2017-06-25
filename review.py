from Tkinter import *
import printer 
import comp
import connectdb as cdb
import tkMessageBox as tmb
import calpicker as cp
import tkFileDialog as tfd
import datetime as dt

class Review (Frame):
	def __init__(self,parent=None,status=0):
		self.status=status
		if not parent:
			parent=Toplevel()
		Frame.__init__(self, parent)
		parent.minsize(width=900,height=600)
		f1=Frame(self,height=100,width=800,bd=2,relief=SUNKEN)
		f1.pack(side=TOP,fill=X)
		self.f1=f1
		f1.pack_propagate(0)
		
		f2=Frame(self, width=250,height=550,bd=2,relief=SUNKEN)
		f2.pack(side=LEFT,fill=Y)
		f2.fr=None
		self.f2=f2
		f2.pack_propagate(0)

		f3=Frame(self,bd=1,relief=RIDGE,width=550)
		f3.pack(fill=BOTH,expand=1)
		sb=Scrollbar(f3)
		sb.pack(side=RIGHT,fill=Y)
		self.canvas=Canvas(f3,yscrollcommand=sb.set)
		self.canvas.pack(fill=BOTH,expand=1)
		sb.config(command=self.canvas.yview)
		self.f3=f3

		self.pack()
		self.packoptions()
		self.lines=[]

	def packoptions(self):
		Button(self.f1,text="Sale",command=lambda:self.showOptions("sale")).pack(side=LEFT)
		Button(self.f1,text="Sale2",command=lambda:self.showOptions("sale2")).pack(side=LEFT)
		Button(self.f1,text="Stock",command=lambda:self.showOptions("stock")).pack(side=LEFT)
		Button(self.f1,text="Purchase",command=lambda:self.showOptions("purchase")).pack(side=LEFT)
		Button(self.f1,text="Bills",command=lambda:self.showOptions("bills")).pack(side=LEFT)

		if self.status=="admin":
			Button(self.f1,text="Print",command=self.printlines).pack(side=RIGHT)
			Button(self.f1,text="Save",command=self.savelines).pack(side=RIGHT)

	def showOptions(self,selection):
		f=self.f2
		if f.fr:
			f.fr.pack_forget()
		if selection=="sale":
			fr=self.packdruggroup(f)
			ft=Frame(fr,bd=1,relief=RIDGE)
			ft.pack(pady=5,fill=X)
			date=BooleanVar()
			Checkbutton(ft,text="Aggregate by date",variable=date).pack()
			Label(ft,text="from").pack(side=LEFT)
			d=dt.date.today()
			dd=dt.date(day=1,month=d.month,year=d.year)
			cb1=cp.Calbutton(ft,inidate=dd)
			cb1.pack(side=LEFT)
			Label(ft,text="to").pack(side=LEFT)
			cb2=cp.Calbutton(ft)
			cb2.pack(side=LEFT)

			ft=Frame(fr,bd=1,relief=RIDGE)
			ft.pack(pady=5,fill=X)
			doc=BooleanVar()			
			Checkbutton(ft,text="Aggregate by doc",variable=doc).pack()
			dr=comp.myComp2(ft,listitems=[],listheight=3)
			dr.pack()
			self.loaddocs(dr)

			ft=Frame(fr,bd=1,relief=RIDGE)
			ft.pack(pady=5,fill=X)
			countoramount=IntVar()
			Radiobutton(ft,text="count",value=1,variable=countoramount).pack(padx=10,pady=5,side=LEFT)
			Radiobutton(ft,text="amount",value=2,variable=countoramount).pack(padx=10,pady=5,side=LEFT)
			countoramount.set(2)

			Button(fr,text="Load",command=lambda g=fr.g,d=fr.d,date=date,doc=doc,dr=dr,d1=cb1,d2=cb2,cnt=countoramount: self.showsale(g,d,date,doc,dr,d1,d2,cnt)).pack(padx=20)
			
		elif selection=="sale2":
			fr=self.packdruggroup(f)
			ft=Frame(fr,bd=1,relief=RIDGE)
			ft.pack(pady=5,fill=X)
			Label(ft,text="from").pack(side=LEFT)
			d=dt.date.today()
			dd=dt.date(day=1,month=d.month,year=d.year)
			cb1=cp.Calbutton(ft,inidate=dd)
			cb1.pack(side=LEFT)
			Label(ft,text="to").pack(side=LEFT)
			cb2=cp.Calbutton(ft)
			cb2.pack(side=LEFT)

			Button(fr,text="Load",command=lambda g=fr.g,d=fr.d,d1=cb1,d2=cb2: self.showsale2(g,d,d1,d2)).pack(padx=20)
			
		elif selection=="stock":
			fr=self.packdruggroup(f)
			fr.opt=opt=IntVar()
			Radiobutton(fr,text="Low Stock",variable=opt,value=0).pack(pady=10)
			Radiobutton(fr,text="Slow moving",variable=opt,value=1).pack(pady=10)
			Radiobutton(fr,text="Expired(ing)",variable=opt,value=2).pack(pady=10)
			Radiobutton(fr,text="None",variable=opt,value=3).pack(pady=10)
			opt.set(3)
			Button(fr,text="Load",command=lambda g=fr.g,d=fr.d,opt=fr.opt : self.showstock(g,d,opt)).pack(padx=20,pady=5)

		elif selection=="purchase":
			fr=self.packdruggroup(f)
			ft=Frame(fr)
			ft.pack(pady=10,padx=10)
			Label(ft,text="stockist").pack(side=LEFT,pady=20,padx=10)		
			st=comp.myComp2(ft,listitems=[])
			st.pack()
			self.loadstockists(st)
			ft=Frame(fr)
			ft.pack(pady=10,padx=10)
			Label(ft,text="time period").pack(side=LEFT,pady=20,padx=10)
			ft.timeperiod=IntVar()
			Radiobutton(ft,variable=ft.timeperiod,text="one week",value=1).pack(side= TOP, pady=2,padx=10)
			Radiobutton(ft,variable=ft.timeperiod,text="one month",value=2).pack(side= TOP, pady=2,padx=10)
			Radiobutton(ft,variable=ft.timeperiod,text="six months",value=3).pack(side= TOP, pady=2,padx=10)
			Radiobutton(ft,variable=ft.timeperiod,text="one year",value=4).pack(side= TOP, pady=2,padx=10)
			Radiobutton(ft,variable=ft.timeperiod,text="all time",value=5).pack(side= TOP, pady=2,padx=10)
			ft.timeperiod.set(3)
			Button(fr,text="Load",command=lambda g=fr.g,d=fr.d,st=st,t=ft: self.showpurchase(g,d,st,t)).pack(pady=5,padx=20)

		elif selection=="bills":
			f.fr=fr=Frame(f,bd=1)
			fr.pack(side=TOP,padx=5,pady=5)			
			ft=Frame(fr)
			ft.pack(pady=20,fill=X)
			Label(ft,text="From").pack(side=LEFT)
			d=dt.date.today()
			dd=dt.date(day=1,month=d.month,year=d.year)
			d1=cp.Calbutton(ft,inidate=dd)
			d1.pack(side=RIGHT)
			ft=Frame(fr)
			ft.pack(pady=20,fill=X)
			Label(ft,text="To").pack(side=LEFT)
			d2=cp.Calbutton(ft)
			d2.pack(side=RIGHT)
			optdate=BooleanVar()
			Checkbutton(fr,text="aggregate by date",variable=optdate).pack(pady=20)
			Button(fr,text="Load",command=lambda d1=d1,d2=d2,op1=optdate:self.showbills(d1,d2,op1)).pack(pady=5)

	def showbills(self,d1,d2,op1):
		d1=d1.get()
		d2=d2.get()
		optdate=op1.get()
		cur=cdb.Db().connection().cursor()
		if not optdate:
			sql="select bill.id, bill.name, bill.net, bill.date, doc.name from bill join doc on bill.doc=doc.id where bill.date >= str_to_date(\"{}\",\"{}\") and bill.date <= str_to_date(\"{}\",\"{}\") order by bill.id;".format(d1,"%d-%b-%y",d2,"%d-%b-%y")
			format=" {:6.0f}  {:15.15s}  {:7.2f}  {:%d-%b-%y}  {:15.15s}"
			titlefields=("Bill","Patient","amount","date","doctor")
			title=" {:6.6s}  {:15.15s}  {:7.7s}  {:9.9s}  {:15.15s}".format(*titlefields)
		else:
			sql="select bill.date, min(bill.id),max(bill.id),sum(bill.net) from bill where bill.date >= str_to_date(\"{}\",\"{}\") and bill.date <= str_to_date(\"{}\",\"{}\") group by bill.date order by bill.id;".format(d1,"%d-%b-%y",d2,"%d-%b-%y")
			format=" {:%d-%b-%y}  {:7.0f}  {:7.0f}  {:10.2f}"
			titlefields=("date","from","to","amount")
			title=" {:9.9s}  {:7.7s}  {:7.7s}  {:10.10s}".format(*titlefields)
			
		self.fillCanvas(sql,format,titlefields,title) 

	def showpurchase(self,g,d,s,t):
		gr=g.get()[1]
		dr=d.get()[1]
		st=s.get()[1]
		tm=t.timeperiod.get()
		print gr,dr,st,tm
		templist=[" 7 day "," 1 month ", " 6 month ", " 1 year "]
		cur=cdb.Db().connection().cursor()
		if dr>-1:
			sql=("select stockist.name,purchase.date,stock.start_count,stock.buy_price,stock.price * (1-(stock.discount/100)+(stock.tax/100)) " )
			format=" {:15.15s} {:%b,%y} {:5.0f} {:7.2f} {:7.2f}"
			tf=("stockist","date","count","cost","price")
			tl=" {:15.15s} {:6.6s} {:5.5s} {:7.7s} {:7.7s}".format(*tf)
		else:
			sql = ("select drug.name, sum(stock.start_count), avg(stock.buy_price),avg(stock.price * (1-(stock.discount/100)+(stock.tax/100)) )" )
			format=" {:15.15s} {:5.0f} {:7.2f} {:7.2f}"
			tf=("drug","count","cost","price")
			tl=" {:15.15s} {:5.5s} {:7.7s} {:7.7s}".format(*tf)
			
		sql+=(" from drug join stock on drug.id=stock.drug_id join purchase on purchase.id=stock.purchase_id join bill on bill.id=purchase.bill "
			" join stockist on purchase.stockist=stockist.id ")
		whered=False
		if dr>-1:
			sql+=" where drug.id={} ".format(dr)
			whered=True
		elif gr>-1:
			sql +=" where drug.id in (select drug from druggroup where groupid={}) ".format(gr)
			whered=True
		if st>-1:
			sql+= (" and " if whered else  " where ")+" stockist.id={}".format(st)
			whered=True
		if tm!=5:
			sql += (" and "if whered else " where ")+" purchase.date>curdate() - interval "+templist[tm-1]
		if dr==-1:
			sql += " group by drug.id order by drug.name ;"
		else :
			sql += " order by stockist.name, purchase.date ;"
		print sql
		self.fillCanvas(sql,format,tf,tl)

	def loadstockists(self,comp):
		cur=cdb.Db().connection().cursor()
		cur.execute("select * from stockist order by name;")
		rows=cur.fetchall()
		items=[["all",-1]]
		for r in rows:
			items.append([r[1],r[0]])
		comp.changelist(items)

	def packdruggroup(self,f):
		f.fr=fr=Frame(f,bd=1)
		fr.pack(side=TOP,padx=5,pady=5)
		ft=Frame(fr)
		ft.pack(padx=10,pady=10)
		Label(ft,text="group").pack(side=LEFT,pady=20,padx=10)
		g=comp.myComp2(ft,listitems=[])
		g.pack()
		ft=Frame(fr)
		ft.pack(padx=10,pady=10)
		Label(ft,text="drug").pack(side=LEFT,pady=20,padx=10)
		d=comp.myComp2(ft,listitems=[])
		d.pack()
		self.loadgroups(g)
		g.bind("<<listChanged>>",lambda e=None,x=g,y=d:self.groupchanged(e,x,y))
		fr.g=g
		fr.d=d
		return fr
			

	def showstock(self,g,d,op):
		group=g.get()[1]
		drug=d.get()[1]
		opt=op.get()
		checklow=checkslow=checkexp=False
		if opt==0:
			checklow=True		
		elif opt==1:
			checkslow=True
		elif opt==2:
			checkexp=True
		cur=cdb.Db().connection().cursor()
		if checklow:
			sql=("select drug.name, sum(stock.cur_count) as cur_count,saletable.sale, purchasetable.stockist from  drug" 					" join stock on drug.id=stock.drug_id left join (select stock.drug_id as drugid, sum(sale.count) as sale from stock join sale on" 					" sale.stock=stock.id join bill on bill.id=sale.bill where bill.date>curdate()-interval 30 day group by drugid) saletable on" 					" drug.id=saletable.drugid join (select drug.id as drugid,stockist.name as stockist, stockist.id as stockistid from drug"
				" join (select * from stock order by id desc)st on st.drug_id=drug.id join purchase on purchase.id=st.purchase_id join "
				"stockist on purchase.stockist=stockist.id group by drug.id ) purchasetable on drug.id=purchasetable.drugid "
				"where stock.cur_count>0 and stock.cur_count< saletable.sale/6 ")
			format=" {:20.20s} {:6.0f} {:6.0f} {:10.10s}"
			tf=("drug","stock","sale(30d)","stockist")
			tl=" {:20.20s} {:6.6s} {:6.6s} {:10.10s}".format(*tf)
			
		elif checkslow:
			sql=("select drug.name, sum(stock.cur_count) as cur_count,saletable.sale,min(stock.expiry) as expiry from drug join stock on" 					" drug.id=stock.drug_id left join (select stock.drug_id as drugid, sum(sale.count) as sale from stock join sale on" 					" sale.stock=stock.id join bill on bill.id=sale.bill where bill.date>curdate()-interval 30 day group by drugid) saletable on" 					" drug.id=saletable.drugid where stock.cur_count>0 and stock.cur_count>(datediff(expiry,curdate())-50)*saletable.sale/30")
			format=" {:20.20s}   {:6.0f}  {:6.0f}    {:%b-%y}"
			tf=("drug","stock","sale","expiry")
			tl=" {:20.20s}   {:6.6s}  {:6.6s}    {:6.6s}".format(*tf)
		elif checkexp:
			sql=("select drug.name,stock.cur_count,stock.expiry from drug join stock on"
				" drug.id=stock.drug_id where stock.cur_count>0 and stock.expiry < curdate()+interval 30 day ")
			format=" {:20.20s}   {:6.0f}    {:%b-%y}"
			tf=("drug","stock","expiry")
			tl=" {:20.20s}   {:6.6s}    {:6.6s}".format(*tf)
		else:
			sql=("select drug.name, sum(stock.cur_count) as cur_count, min(stock.expiry) as expiry "
				"from stock join drug on drug.id=stock.drug_id where stock.cur_count>0 " )
			format=" {:20.20s}   {:6.0f}    {:%b-%y}"
			tf=("drug","stock","expiry")
			tl=" {:20.20s}   {:6.6s}    {:6.6s}".format(*tf)
		if drug>-1:
			sql+= " and drug.id="+str(drug)
		elif group>-1:
			sql+= " and drug.id in (select drug from druggroup where druggroup.groupid="+str(group)+")"
		if checklow:
			sql += " group by drug.id order by purchasetable.stockist,drug.name; "
		elif checkexp:
			sql+=" and expiry> curdate() group by drug.id order by drug.name;"
		else:
			sql+=" group by drug.id order by drug.name;"
		self.fillCanvas(sql,format,tf,tl)

	def groupchanged(self,e,g,d):
		cur=cdb.Db().connection().cursor()
		group=g.get()[1]
		sql="select * from drug "
		if group >-1:
			sql+=" where drug.id in (select drug from druggroup where groupid="+str(group)+") "
		sql+=" order by drug.name;"
		cur.execute(sql)
		rows=cur.fetchall()
		items=[["all",-1]]
		for r in rows:
			items.append([r[1],r[0]])
		d.changelist(items)

	def loaddocs(self,dr):
		cur=cdb.Db().connection().cursor()
		cur.execute("select * from doc order by name;")
		lst=[["all",-1]]
		rows=cur.fetchall()
		for r in rows:
			lst.append([r[1],r[0]])
		dr.changelist(lst)

	def loadgroups(self,c):
		cur=cdb.Db().connection().cursor()
		cur.execute("select * from groups order by name;")
		lst=[["all",-1]]
		rows=cur.fetchall()
		for r in rows:
			lst.append([r[1],r[0]])
		c.changelist(lst)
				
	def showsale(self,g,d,date,doc,dr,d1,d2,cnt):
		group=g.get()[1]
		drug=d.get()[1]
		doctor=dr.get()[1]
		date1=d1.get()
		date2=d2.get()
		sortbydate=date.get()
		sortbydoc=doc.get()
		countoramount=cnt.get()
		cur=cdb.Db().connection().cursor()
		formatstring="{:15.15s} -"
		countformat="{:6f}"
		selectstring=" drug.name "
		groupstring=" drug.id "
		countstring=" sum(sale.count) "

		if drug>-1:
			wheredrug=" and drug.id={} ".format(drug)
		elif group>-1:
			wheredrug=" and drug.id in (select drug from druggroup where groupid={}) ".format(group)
		else:
			wheredrug=""
		if countoramount==2:
			countstring=" sum(sale.count*(stock.price*(100-stock.discount)*(100+stock.tax)/10000)) "
			countformat=" {:7.2f}"
		if sortbydate==1:
			datestring=" ,bill.date "
	 		dateorder=" bill.date, "
			formatstring="{:%d %b,%Y} -"
			selectstring=" bill.date "
			groupstring=" bill.date "
		else :
			datestring=""
			dateorder= ""
		if sortbydoc==1:
			docstring=" ,doc.name "
			groupstring=" doc.id "
			selectstring=" doc.name "
		else:
			docstring=""
		if doctor>-1:
			wheredoc=" and doc.id ={} ".format(doctor)
		else: wheredoc=""
		formatstring+=countformat

		sql= "select {}, {} from drug join stock on drug.id=stock.drug_id join sale on sale.stock=stock.id join bill on sale.bill = bill.id join doc on doc.id=bill.doc where bill.date> str_to_date(\"{}\",\"{}\") and bill.date< str_to_date(\"{}\",\"{}\") {} {}  group by {} order by {} drug.name {};".format(selectstring,countstring,date1,'%d-%b-%y',date2,'%d-%b-%y', wheredrug,wheredoc,groupstring,dateorder,docstring)

		self.fillCanvas(sql,formatstring)		
		
	def showsale2(self,g,d,d1,d2):
		group=g.get()[1]
		drug=d.get()[1]
		date1=d1.get()
		date2=d2.get()
		cur=cdb.Db().connection().cursor()
		formatstring="{:12.12s}-{:10.10s}-{:4d}-{:18.18s}-{:%d%b}"
		if drug>-1:
			wheredrug=" and drug.id={} ".format(drug)
		elif group>-1:
			wheredrug=" and drug.id in (select drug from druggroup where groupid={}) ".format(group)
		else:
			wheredrug=""
				
		sql="select drug.name,stock.batch,sale.count,bill.name,bill.date from drug join stock on drug.id=stock.drug_id join sale on stock.id=sale.stock join bill on bill.id=sale.bill where bill.date> str_to_date(\"{}\",\"{}\") and bill.date< str_to_date(\"{}\",\"{}\") {} order by drug.name,sale.id".format(date1,'%d-%b-%y',date2,'%d-%b-%y',wheredrug)
		
		self.fillCanvas(sql,formatstring)

	def fillCanvas(self,sql,fmt,titlefields=None,title=None):
		self.canvas.delete(ALL)
		con=cdb.Db().connection()
		cur=con.cursor()
		print sql
		#try:
		cur.execute(sql)
		rows=cur.fetchall()
		#except:
		#	tmb.showerror("Error","check for values",parent=self.master)
		#	return
		i=0
		self.lines=[]
		self.csv=[]
		if title: 
			self.lines.append(title)
			self.canvas.create_text(2,5+i*20,text=title,anchor=NW,font=("FreeMono",10))
			i+=1
		if titlefields: 
			self.csv.append(titlefields)
		for row in rows:
			line=fmt.format(*row)
			self.lines.append(line)
			self.csv.append(row)
			self.canvas.create_text(2,5+i*20,text=line,anchor=NW,font=("FreeMono",10))
			i+=1
		self.canvas.config(scrollregion=self.canvas.bbox(ALL))

	def printlines(self):
		printer.printinfo(self.lines)
	
	def savelines(self):
		filename=tfd.asksaveasfilename(parent=self.master,title="Select file to save",initialdir="./saved")
		if not filename:
			return		
		fil=open(filename,'w')
		for l in self.csv:
			l=map(str,l)
			fil.write(','.join(l)+"\r\n")
	
if __name__=="__main__":
	t=Tk()
	a=Review(t)
	a.mainloop()
