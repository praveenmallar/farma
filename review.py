from Tkinter import *
import printer 
import comp
import connectdb as cdb
import tkMessageBox as tmb

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

		if self.status=="admin":
			Button(self.f1,text="Print",command=self.printlines).pack(side=RIGHT)

	def showOptions(self,selection):
		f=self.f2
		if f.fr:
			f.fr.pack_forget()
		if selection=="sale":
			f.fr=fr=Frame(f,bd=1)
			fr.pack(side=TOP,padx=5,pady=5)
			v1=IntVar()
			v1.set(0)
			v2=IntVar()
			v2.set(0)
			frr=Frame(fr)
			frr.pack()
			Label(frr,text="From").pack(side=LEFT)
			comp.NumEntry(frr,textvariable=v1,width=8).pack(side=LEFT)
			Label(frr,text="To").pack(side=LEFT)
			comp.NumEntry(frr,textvariable=v2,width=8).pack(side=LEFT)
			b=Button(frr,text="Show")
			b.pack(side=LEFT)
			cur=cdb.Db().connection().cursor()
			cur.execute("select name from doc order by name;")
			rows=cur.fetchall()
			lb=Listbox(fr,selectmode=SINGLE)
			lb.pack()
			lb.insert(END,"")
			for r in rows:
				lb.insert(END,r[0])
			lb.selection_set(0)
			b.config(command=lambda x=v1,y=v2,z=lb:self.showSale("bills",x,y,z))
			
	
	def showSale(self,mode,*args):
		if mode=="bills":
			v1=args[0].get()
			v2=args[1].get()
			v3=args[2]
			v3=v3.get(v3.curselection())
			if len(v3.strip())>0:
				docstring=" and doc.name= '"+v3+"' "
			else :
				docstring=""
			sql="select bill.id, bill.name as patient, doc.name as doc, bill.date, bill.net from bill join doc on bill.doc=doc.id where bill.id>="+str(v1)+" and bill.id<="+str(v2)+docstring+" order by bill.id;"
			format="{:<6d} {:15.14s} {:12.10s} {:%d-%b,%y} {:8.2f}"
			self.fillCanvas(sql,format)
			

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
		for row in rows:
			line=fmt.format(*row)
			self.lines.append(line)
			self.canvas.create_text(2,5+i*20,text=line,anchor=NW,font=("FreeMono",10))
			i+=1
		self.canvas.config(scrollregion=self.canvas.bbox(ALL))

	def printlines(self):
		printer.printinfo(self.lines)
			
	
if __name__=="__main__":
	a=Review()
	a.mainloop()
