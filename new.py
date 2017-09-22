import Tkinter as tk
import connectdb as cdb
from tkMessageBox import askokcancel,showinfo

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
		oldtx=self.lb.get(self.lb.curselection()[0])
		newtx=self.ed.get()
		if not askokcancel("Confirm","Change "+oldtx + " to " + newtx + "?",parent=self.master):
			return
		cursor=self.db.cursor()
		sql="update "+self.table+" set "+self.field+"=%s where "+self.field+"=%s;"
		if cursor.execute(sql,[newtx,oldtx]):
			self.ed.set("")
			self.refreshlist()
			
	def listboxchanged(self,e):
		self.ed.set(self.lb.get(self.lb.curselection()[0]))
	
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

class addDoc(addNew):
	def __init__(self, parent=None, table="doc",field="name",title="Add Doctor"):
		addNew.__init__(self,parent,table,field,title)
			
class addStockist(addNew):
	def __init__(self, parent=None, table="stockist",field="name",title="Add Stockist"):
		addNew.__init__(self,parent,table,field,title)
		
class addDrug(addNew):
	def __init__(self, parent=None, table="drug",field="name",title="Add Drug"):
		addNew.__init__(self,parent,table,field,title)
		self.mfcrs=[]
		cur=self.db.cursor()
		cur.execute("select name from manufacture order by name;")
		fs=cur.fetchall()
		for f in fs:
			self.mfcrs.append(f[0])
		self.mfcr=tk.StringVar()
		self.mfcr.set(self.mfcrs[0])
		tk.Label(self.mfcrFrame,text="Manufacturer").grid(row=1,column=1)
		tk.OptionMenu(self.mfcrFrame,self.mfcr,*self.mfcrs).grid(row=1,column=2)
	
	def listboxchanged(self,e):
		addNew.listboxchanged(self,e)
		cur=self.db.cursor()
		dr=self.lb.get(self.lb.curselection()[0])
		print dr
		cur.execute("select name from manufacture where id=(select manufacture from drug where name=%s);",(dr))
		r=cur.fetchone()
		self.mfcr.set(r[0])

class adder(tk.Frame):
	def __init__(self,parent=None):
		if not parent:
			t=tk.Toplevel()
			parent=t
		tk.Frame.__init__(self,parent)
		addDrug(self).pack(side="left")
		addDoc(self).pack(side="left")
		addStockist(self).pack(side="left")
		self.pack()

if __name__==	"__main__":
	t=tk.Tk()
	ad=addDrug(t)
	ad.mainloop()
