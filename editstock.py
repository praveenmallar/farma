from Tkinter import *
import password,comp
import tkMessageBox
import connectdb as cdb
import calpicker as cal

class EditStock(Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.pack()
		con=cdb.Db().connection()
		cur=con.cursor()		
		f1=Frame(self)
		f1.pack()
		f=Frame(f1)
		f.pack(side=LEFT)
		Label(f,text="drug").pack()
		sql="select name from drug;"
		cur.execute(sql)
		rows=cur.fetchall()
		items=[]
		for row in rows:
			items.append(row[0])
		self.drug=comp.myComp(f,listitems=items)
		self.drug.pack()
		Button(f1,text="search",command=self.refresh).pack(side=LEFT)

		f2=Frame(self)
		f2.pack(side=LEFT)
		sb=Scrollbar(f2)
		sb.pack(side=RIGHT,fill=Y)
		self.can=Canvas(f2,height=400,width=650,bd=1,relief=SUNKEN,yscrollcommand=sb.set)
		self.can.pack()
		sb.config(command=self.can.yview)

		f3=Frame(self)
		f3.pack(side=LEFT)
		sb=Scrollbar(f3)
		sb.pack(side=RIGHT,fill=Y)
		self.editcan=Canvas(f3,relief=RAISED,yscrollcommand=sb.set,height=400,width=400)
		self.editcan.pack()
		sb.config(command=self.editcan.yview)
		
			
	def refresh(self):
		drug=self.drug.get()
		self.can.delete(ALL)
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="select drug.name,stock.id,stock.start_count, stock.cur_count,stock.batch,stock.price, stock.cgstp, stock.sgstp, stock.discount, stock.expiry from drug join stock on drug.id=stock.drug_id where drug.name=%s order by stock.id desc;"
		cur.execute(sql,[drug])
		rows=cur.fetchall()
		i=1
		f=Frame(self.can,bd=1)
		Label(f,text="drug",width=20).pack(side=LEFT)
		Label(f,text="batch",width=10).pack(side=LEFT)
		Label(f,text="count",width=5).pack(side=LEFT)
		Label(f,text="stock",width=5).pack(side=LEFT)
		Label(f,text="price",width=7).pack(side=LEFT)
		Label(f,text="cgst",width=4).pack(side=LEFT)
		Label(f,text="sgst",width=4).pack(side=LEFT)
		Label(f,text="disc",width=4).pack(side=LEFT)
		Label(f,text="expiry",width=10).pack(side=LEFT)
		self.can.create_window(5,5,window=f,anchor=NW)
		for row in rows:
			f=Frame(self.can,bd=1,relief=RIDGE)
			Label(f,text=row[0],width=20).pack(side=LEFT)
			Label(f,text=row[4],width=10).pack(side=LEFT)
			Label(f,text=row[2],width=5).pack(side=LEFT)
			Label(f,text=row[3],width=5).pack(side=LEFT)
			Label(f,text=row[5],width=7).pack(side=LEFT)
			Label(f,text=row[6],width=4).pack(side=LEFT)
			Label(f,text=row[7],width=4).pack(side=LEFT)
			Label(f,text=row[8],width=4).pack(side=LEFT)
			Label(f,text=row[9],width=10).pack(side=LEFT)
			Button(f,text="edit",command=lambda x=row[1]:self.edit(x)).pack(side=LEFT)
			self.can.create_window(5,5+i*30,window=f,anchor=NW)
			i+=1
		self.can.update_idletasks()
		self.can.config(scrollregion=self.can.bbox(ALL))
		self.edit(0)
	
	def edit(self,id):
		self.editcan.delete(ALL)
		if id==0:
			return
		if not password.askpass("admin"):
			return()
		f=Frame(self.editcan)
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="select drug.name,stock.id,stock.start_count, stock.cur_count,stock.batch,stock.price, stock.cgstp,stock.sgstp, stock.discount, stock.expiry from drug join stock on drug.id=stock.drug_id where stock.id=%s;"
		cur.execute(sql,[id])
		row=cur.fetchone()
		Label(f,text="drug").grid(row=0,column=0,sticky=E,padx=10,pady=5)
		Label(f,text=row[0]).grid(row=0,column=1,sticky=W,padx=10,pady=5)
		Label(f,text="batch").grid(row=1,column=0,sticky=E,padx=10,pady=5)
		Label(f,text=row[4]).grid(row=1,column=1,sticky=W,padx=10,pady=5)
		Label(f,text="stock").grid(row=2,column=0,sticky=E,padx=10,pady=5)
		f.count=IntVar()
		f.count.set(row[3])		
		Entry(f,textvariable=f.count,width=5).grid(row=2,column=1,sticky=W,padx=10,pady=5)
		Label(f,text="price").grid(row=3,column=0,sticky=E,padx=10,pady=5)
		f.price=DoubleVar()
		f.price.set(row[5])		
		Entry(f,textvariable=f.price,width=5).grid(row=3,column=1,sticky=W,padx=10,pady=5)
		Label(f,text="CGST").grid(row=4,column=0,sticky=E,padx=10,pady=5)
		f.cgst=DoubleVar()
		f.cgst.set(row[6])		
		Entry(f,textvariable=f.cgst,width=5).grid(row=4,column=1,sticky=W,padx=10,pady=5)
		Label(f,text="SGST").grid(row=5,column=0,sticky=E,padx=10,pady=5)
		f.sgst=DoubleVar()
		f.sgst.set(row[7])		
		Entry(f,textvariable=f.sgst,width=5).grid(row=5,column=1,sticky=W,padx=10,pady=5)
		Label(f,text="discount").grid(row=6,column=0,sticky=E,padx=10,pady=5)
		f.discount=DoubleVar()
		f.discount.set(row[8])		
		Entry(f,textvariable=f.discount,width=5).grid(row=6,column=1,sticky=W,padx=10,pady=5)
		Label(f,text="expiry").grid(row=7,column=0,sticky=E,padx=10,pady=5)
		calpicker=cal.Calbutton(f,inidate=row[9])
		calpicker.grid(row=7,column=1,sticky=W)
		Button(f,text="save",command=lambda:self.savestock(row[1],f.count.get(),f.price.get(),f.cgst.get(),f.sgst.get(),f.discount.get(),calpicker.get())).grid(row=8,column=1,sticky=W,padx=10,pady=5)
		self.editcan.create_window(1,1,window=f,anchor=NW)	

	def savestock(self,id,count,price,cgstp,sgstp,discount,date):
		con=cdb.Db().connection()
		cur=con.cursor()
		cur.execute("select str_to_date('"+date+"','%d-%b-%y');")
		r=cur.fetchone()
		date=r[0]
		sql="update stock set cur_count=%s,price=%s,cgstp=%s,sgstp=%s,discount=%s,expiry=%s where id=%s;"
		cur.execute(sql,(count,price,cgstp,sgstp,discount,date,id))
		con.commit()
		tkMessageBox.showinfo("Done","Stock saved",parent=self.master)	
		self.refresh()	

if __name__=="__main__":
	EditStock(Tk()).mainloop()
