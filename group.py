from Tkinter import *
import comp
import connectdb as cdb

class Group(Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Tk()
		Frame.__init__(self,parent)
		self.pack()
		self.groups=comp.myComp2(self,listitems=[],listheight=5)
		self.drugs=comp.myComp2(self,listitems=[],listheight=5)
		self.druggroup=comp.myComp2(self,listitems=[],listheight=5)
		self.druggroup_label=Label(self,text="Drugs in Group")
		f=Frame(self)

		Label(self,text="Group").grid(row=0,column=0)
		self.druggroup_label.grid(row=0,column=1)
		Label(self,text="Drug").grid(row=0,column=3)
		self.groups.grid(row=1,column=0,padx=5,pady=5)
		self.druggroup.grid(row=1,column=1,padx=5,pady=5)		
		f.grid(row=1,column=2,padx=5,pady=5)
		self.drugs.grid(row=1,column=3,padx=5,pady=5)

		Button(f,text="<<",command=self.add).pack(pady=20)
		Button(f,text=">>",command=self.remove).pack(pady=20)

		self.groups.bind("<<listChanged>>",self.loadgroupdrugs)
		
		self.loadgroups()
		self.loaddrugs()
	
	def loadgroups(self):
		index=self.groups.index()
		if not index:
			index=0
		cur=cdb.Db().connection().cursor()
		cur.execute("select * from groups order by name;")
		rows=cur.fetchall()
		items=[]
		for r in rows:
			items.append([r[1],r[0]])
		self.groups.changelist(items)
		self.groups.see(index)	

	def loaddrugs(self):
		pass

	def loadgroupdrugs(self):
		pass

	def add(self):
		pass
	def remove(self):
		pass

if __name__=="__main__":
	g=Group()
	g.mainloop()
