import Tkinter as tk
import connectdb as cdb
from tkMessageBox import askokcancel,showinfo
from comp import myComp2

class addNew(tk.Frame):

	def __init__(self,parent=None,table="doc",field="name",title="Add New"):	
		tk.Frame.__init__(self,parent)
		self.search=tk.StringVar()
		tk.Entry(self,textvariable=self.search).pack(side=tk.TOP,fill=tk.X)
		self.search.trace("w",self.searchtx)
		tk.Label(self,text=title).pack(side=tk.TOP)
		f=tk.Frame(self)
		f.pack(fill=tk.X)
		self.lb=tk.Listbox(f)
		sb=tk.Scrollbar(f,orient=tk.VERTICAL)
		self.lb.config(yscrollcommand=sb.set)
		sb.config(command=self.lb.yview)
		sb.pack(side=tk.RIGHT,fill=tk.Y)
		self.lb.pack(fill=tk.BOTH,expand=1)
		self.lb.bind("<<ListboxSelect>>",self.listboxchanged)
		self.mfcrFrame=tk.Frame(self)
		self.mfcrFrame.pack(fill=tk.X)
		fr=tk.Frame(self)
		self.ed=tk.StringVar()
		edt=tk.Entry(fr,textvariable=self.ed)
		delb=tk.Button(fr,text="Edit ",command=self.edit)
		delb.bind('<Return>',lambda event:self.edit())
		edt.pack(side=tk.LEFT)
		delb.pack()
		fr.pack()
		self.tx=tk.StringVar()
		fr=tk.Frame(self)
		self.en=tk.Entry(fr,textvariable=self.tx)
		btn=tk.Button(fr,text="Add",command=self.addnew,default="active")
		btn.bind('<Return>',lambda event:self.addnew())		
		self.en.pack(side=tk.LEFT)
		btn.pack()
		fr.pack()
		self.en.focus()
		self.table=table
		self.field=field
		self.db=cdb.Db().connection()
		self.refreshlist()
		self.pack(padx=10,pady=10)

	def addnew(self):
		cursor=self.db.cursor()
		newentry = self.tx.get()
		if askokcancel("Confirm", "Do you want to insert - {0}".format(newentry),parent=self.master):
			cursor.execute ("select * from "+self.table+" where "+self.field+"='"+newentry+"'")
			if cursor.rowcount==0:		
				cursor.execute("insert into "+self.table+"("+self.field+") values('"+self.tx.get()+"');")
				self.db.commit()
				showinfo("Done",newentry+" inserted!",parent=self.master)
		self.refreshlist()
		self.tx.set("")
		self.en.focus()
	
	def edit(self):
		oldtx=""
		sel=self.lb.get(self.lb.curselection())
		if len(sel)>0:
			oldtx=sel
		newtx=self.ed.get()
		if not askokcancel("Confirm","Change "+oldtx + " to " + newtx + "?",parent=self.master):
			return
		cursor=self.db.cursor()
		sql="update "+self.table+" set "+self.field+"=%s where "+self.field+"=%s;"
		if cursor.execute(sql,[newtx,oldtx]):
			self.ed.set("")
			self.refreshlist()
		self.db.commit()
		self.ed.set("")
		self.refreshlist()
			
	def listboxchanged(self,e):
		tx=""
		sel=self.lb.curselection()
		if len(sel)>0:
			tx=self.lb.get(sel[0])
		self.ed.set(tx)
	
	def searchtx(self,a,b,c):
		tx=self.search.get()
		lst=self.lb.get(0,"end")
		i=0
		for f in lst:	
			if f.lower().find(tx.lower())==0:
				self.lb.see(i)
				return
			i+=1
			
	def refreshlist(self):
		cursor = self.db.cursor()
		cursor.execute("select * from "+self.table+" order by "+self.field)
		result = cursor.fetchall()
		self.lb.delete(0,tk.END)
		for row in result:
			self.lb.insert(tk.END,row[1])

		
class addDrug(addNew):
	def __init__(self, parent=None, table="drug",field="name",title="Add Drug"):
		addNew.__init__(self,parent,table,field,title)
		self.mfrs=[(" ",-1)]
		cur=self.db.cursor()
		cur.execute("select name,id from manufacture order by name;")
		fs=cur.fetchall()
		for f in fs:
			self.mfrs.append((f[0],f[1]))
		tk.Label(self.mfcrFrame,text="Manufacturer").grid(row=1,column=1)
		self.comp=myComp2(self.mfcrFrame,listitems=self.mfrs,listheight=2)
		self.comp.grid(row=1,column=2)
		
	def listboxchanged(self,e):
		addNew.listboxchanged(self,e)
		cur=self.db.cursor()
		dr=""
		sel=self.lb.curselection()
		if len(sel)>0:
			dr=self.lb.get(sel[0])
		cur.execute("select name from manufacture where id in (select manufacture from drug where name=%s);",[dr])
		if cur.rowcount==1:
			r=cur.fetchone()
			r=r[0]
		else:
			r=""
		self.comp.text.set(r)

	def edit(self):
		drg=self.ed.get()
		addNew.edit(self)
		mfcr=self.comp.get()
		if mfcr:
			mfcr=mfcr[1]
		else:
			mfcr=0
		cur=self.db.cursor()
		cur.execute("update drug set manufacture=%s where name=%s",(mfcr,drg))
		self.db.commit()
		
		
class adder(tk.Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=tk.Toplevel()
		tk.Frame.__init__(self,parent)
		addNew(self, table="doc",field="name",title="Add Doctor").pack(side="left")
		addNew(self, table="stockist",field="name",title="Add Stockist").pack(side="left")
		addDrug(self).pack(side="left")
		addNew(self, table="manufacture", field="name",title="Add Manufacturer").pack(side="left")
		self.pack()

if __name__==	"__main__":
	t=tk.Tk()
	ad=adder(t)
	ad.mainloop()
