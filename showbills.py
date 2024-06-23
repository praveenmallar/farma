from tkinter import *
import password
import printer as printbill

class ShowFiles(Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		f=Frame(self)
		f.pack()
		Button(f,text="<",command=lambda:self.seekfile(1)).pack(side=LEFT)
		Label(f,text="Bills").pack(side=LEFT)
		Button(f,text=">",command=lambda:self.seekfile(2)).pack(side=LEFT)
		f2=Frame(self)
		f2.pack()
		sb=Scrollbar(f2)
		sb.pack(side=RIGHT,fill=Y)
		self.canvas=Canvas(f2,bd=1,relief=SUNKEN,yscrollcommand=sb.set,width=400,height=400	)
		self.canvas.pack()
		sb.config(command=self.canvas.yview)
		Button(self,text="print",command=self.printout,height=3,width=10).pack(side=RIGHT,padx=20,pady=20)
		self.lines=[]
		self.file=open("bills.txt","r")
		self.offsets=[]
		offset=0
		for line in self.file:
			self.offsets.append(offset)
			offset+=len(line)
		self.file.seek(0)
		self.pack()
		self.offset=len(self.offsets)-2
		self.seekfile(2)
		
	def seekfile(self,dir):
		if dir==1 and self.offset>0:
			self.offset-=1
		if dir==2 and self.offset<len(self.offsets)-1:
			self.offset+=1
		self.lines=[]
		self.file.seek(self.offsets[self.offset])
		line=self.file.readline()
		self.canvas.delete(ALL)
		lines=line.split("@@")
		i=0
		for line in lines:
			self.lines.append(line)
			self.canvas.create_text(5,5+i*20,text=line,anchor=NW)
			i+=1
		self.canvas.config(scrollregion=self.canvas.bbox(ALL))
	
	def printout(self):
		if len(self.lines)==0:
			return
		if not password.askpass("admin"):
			return
		printbill.printinfo(self.lines)	

if __name__=="__main__":
	f=ShowFiles()
	f.mainloop()
