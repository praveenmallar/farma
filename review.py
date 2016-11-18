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
		parent.minsize(width=800,height=600)
		f1=Frame(self,height=100,width=800,bd=2,relief=SUNKEN)
		f1.pack(side=TOP,fill=X)
		self.f1=f1
		f1.pack_propagate(0)
		
		f2=Frame(self, width=250,height=500,bd=2,relief=SUNKEN)
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
		Button(self.f1,text="Stock",command=lambda:self.showOptions("stock")).pack(side=LEFT)

		if self.status=="admin":
			Button(self.f1,text="Print",command=self.printlines).pack(side=RIGHT)
			Button(self.f1,text="Save",command=self.savelines).pack(side=RIGHT)

	def showOptions(self,selection):
		f=self.f2
		if f.fr:
			f.fr.pack_forget()
		if selection=="sale":
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

			ft=Frame(fr,bd=1,relief=RIDGE)
			ft.pack(pady=5,fill=X)
			date=BooleanVar()
			Checkbutton(ft,text="Aggregate by date",variable=date).pack()
			Label(ft,text="from").pack(side=LEFT)
			cb1=cp.Calbutton(ft)
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

			Button(fr,text="Load",command=lambda g=g,d=d,date=date,doc=doc,dr=dr,d1=cb1,d2=cb2,cnt=countoramount: self.showsale(g,d,date,doc,dr,d1,d2,cnt)).pack(padx=20)

		elif selection=="stock":
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
			checklow=BooleanVar()
			checkslow=BooleanVar()
			checkexp=BooleanVar()
			Checkbutton(fr,text="Low Stock",variable=checklow).pack(pady=10)
			Checkbutton(fr,text="Slow moving",variable=checkslow).pack(pady=10)
			Checkbutton(fr,text="Expired(ing)",variable=checkexp).pack(pady=10)
			Button(fr,text="Load",command=lambda g=g,d=d,low=checklow,slow=checkslow,ex=checkexp : self.showstock(g,d,low,slow,ex)).pack(padx=20,pady=5)

	def showstock(self,g,d,low,slow,exp):
		group=g.get()[1]
		drug=d.get()[1]
		checklow=low.get()
		checkslow=slow.get()
		checkexp=exp.get()
		cur=cdb.Db().connection().cursor()
		if checklow:
			sql="select drug.name, sum(stock.cur_count) as cur_count,saletable.sale,min(stock.expiry) as expiry from drug join stock on drug.id=stock.drug_id left join (select stock.drug_id as drugid, sum(sale.count) as sale from stock join sale on sale.stock=stock.id join bill on bill.id=sale.bill where bill.date>curdate()-interval 30 day group by drugid) saletable on drug.id=saletable.drugid where stock.cur_count>0 and stock.cur_count< saletable.sale/6  "
			format=" {:20.20s}   {:6.0f}  {:6.0f}    exp:{:%b-%y}"
		elif checkslow:
			sql="select drug.name, sum(stock.cur_count) as cur_count,saletable.sale,min(stock.expiry) as expiry from drug join stock on drug.id=stock.drug_id left join (select stock.drug_id as drugid, sum(sale.count) as sale from stock join sale on sale.stock=stock.id join bill on bill.id=sale.bill where bill.date>curdate()-interval 30 day group by drugid) saletable on drug.id=saletable.drugid where stock.cur_count>0 and stock.cur_count>(datediff(expiry,curdate())-50)*saletable.sale/30  "
			format=" {:20.20s}   {:6.0f}  {:6.0f}    exp:{:%b-%y}"
		elif checkexp:
			sql="select drug.name,stock.cur_count,stock.expiry from drug join stock on drug.id=stock.drug_id where stock.cur_count>0 and stock.expiry < curdate()+interval 30 day "			
			format=" {:20.20s}   {:6.0f}    exp:{:%b-%y}"
		else:
			sql="select drug.name, sum(stock.cur_count) as cur_count, min(stock.expiry) as expiry from stock join drug on drug.id=stock.drug_id where stock.cur_count>0 " 
			format=" {:20.20s}   {:6.0f}    exp:{:%b-%y}"
		if drug>-1:
			sql+= " and drug.id="+str(drug)
		elif group>-1:
			sql+= " and drug.id in (select drug from druggroup where druggroup.groupid="+str(group)+")"
		if not checkexp:
			sql+=" and expiry> curdate() group by drug.id order by drug.name;"
		else:
			sql+=" group by drug.id order by drug.name;"
		print sql
		self.fillCanvas(sql,format)

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
		

	def fillCanvas(self,sql,fmt):
		self.canvas.delete(ALL)
		con=cdb.Db().connection()
		cur=con.cursor()
		try:
			cur.execute(sql)
			rows=cur.fetchall()
		except:
			tmb.showerror("Error","check for values",parent=self.master)
			return
		i=0
		self.lines=[]
		self.csv=[]
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
			print l
			l=map(str,l)
			fil.write(','.join(l)+"\r\n")
	
if __name__=="__main__":
	t=Tk()
	a=Review(t)
	a.mainloop()
