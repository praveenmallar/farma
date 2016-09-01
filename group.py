from Tkinter import *
import comp
import connectdb as cdb
import tkMessageBox as tmb

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
		self.druggroup.bind("<<doubleClicked>>",self.remove)
		self.drugs.bind("<<doubleClicked>>",self.add)
		
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
		cur=cdb.Db().connection().cursor()
		cur.execute("select * from drug order by name;")
		rows=cur.fetchall()
		items=[]
		for r in rows:
			items.append([r[1],r[0]])
		self.drugs.changelist(items)
		
	def loadgroupdrugs(self,e=None):
		group=self.groups.get()[1]
		cur=cdb.Db().connection().cursor()
		cur.execute("select drug.name,drug.id,druggroup.groupid,groups.name from drug join druggroup on druggroup.drug=drug.id "\
			" join groups on druggroup.groupid=groups.id where druggroup.groupid=%s;",(group))
		rows=cur.fetchall()
		items=[]
		for r in rows:
			items.append([r[0],[r[1],r[2],r[0],r[3]]])
		self.druggroup.changelist(items)

	def add(self,e=None):
		group=self.groups.get()[1]
		drug=self.drugs.get()[1]
		con=cdb.Db().connection()
		cur=con.cursor()
		cur.execute("insert into druggroup(groupid,drug) values(%s,%s);",(group,drug))
		con.commit()
		self.loadgroups()

	def remove(self,e=None):
		druggroup=self.druggroup.get()[1]
		drugid=druggroup[0]
		groupid=druggroup[1]
		drug=druggroup[2]
		group=druggroup[3]
		if not tmb.askyesno("Confirm","Remove {} from {}?".format(drug,group),parent=self.master):
			return
		con=cdb.Db().connection()
		cur=con.cursor()
		cur.execute("delete from druggroup where drug=%s and groupid=%s;",(drugid,groupid))
		con.commit()
		self.loadgroupdrugs()

if __name__=="__main__":
	g=Group()
	g.mainloop()
