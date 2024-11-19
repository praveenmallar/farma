from tkinter import *
import comp, calpicker
import connectdb as cdb


class CreditNote(Frame):
    def __init__(self, parent=None):
        if not parent:
            parent = Toplevel()
        Frame.__init__(self, parent)
        self.pack()
        f1 = Frame(self)
        f2 = Frame(self, bd=1, relief=SUNKEN)
        sb = Scrollbar(f2)
        sb.pack(side=RIGHT, fill=Y)
        self.canvas = Canvas(f2, height=400, width=300, yscrollcommand=sb.set, relief=SUNKEN)
        self.canvas.pack(fill=BOTH, expand=1)
        sb.config(command=self.canvas.yview)
        cur = cdb.Db().connection().cursor()
        sql = "select * from stockist order by name;"
        cur.execute(sql)
        rows = cur.fetchall()
        stockists = []
        for row in rows:
            stockists.append([row[1], row[0]])
        self.stockists = comp.myComp2(f1, listitems=stockists, listheight=4)
        self.stockists.pack(side=LEFT)
        Button(f1, text="Show", command=lambda: self.showcredits(cur)).pack(side=LEFT)
        self.f3 = Frame(self, bd=1, relief=RIDGE, padx=20, pady=30)
        ff = self.f3
        Label(ff, text="Add New Creditnote", font="Times 12 bold").grid(row=0, column=0, columnspan=2)
        Label(ff, text="Bill number").grid(row=1, column=0)
        Label(ff, text="date").grid(row=2, column=0)
        Label(ff, text="amount").grid(row=3, column=0)
        Button(ff, text="Add", command=self.addcredit).grid(row=4, column=1)
        self.crnumber = IntVar()
        self.crnumber.set(0)
        comp.NumEntry(ff, textvariable=self.crnumber, width=10).grid(row=1, column=1, padx=10, pady=10)
        self.crdate = calpicker.Calbutton(ff)
        self.crdate.grid(row=2, column=1, padx=10, pady=20)
        self.cramount = DoubleVar()
        self.cramount.set(0)
        comp.NumEntry(ff, textvariable=self.cramount, width=10).grid(row=3, column=1, padx=10, pady=20)
        f2.pack(side=RIGHT, fill=X, expand=1)
        f1.pack(side=TOP, padx=10, pady=10)
        self.f3.pack(fill=BOTH, expand=1, side=RIGHT)

    def showcredits(self, cursor=None):
        if not cursor:
            cur = cdb.Db().connection().cursor()
        else:
            cur = cursor
        sql = "select * from purchase where stockist={} and amount<0 order by id desc;".format(self.stockists.get()[1])
        cur.execute(sql)
        rows = cur.fetchall()
        self.canvas.delete(ALL)
        i = 0
        for row in rows:
            line = "{:<10s} {:%d/%b,%y} {:10.2f}".format(row[1], row[3], row[4])
            self.canvas.create_text(2, 10 + i * 20, text=line, anchor=NW)
            i += 1
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))

    def addcredit(self):
        con = cdb.Db().connection()
        cur = con.cursor()
        b = self.crnumber.get()
        s = self.stockists.get()[1]
        d = self.crdate.get()
        a = -(self.cramount.get())
        sql = "insert into purchase(bill,stockist,date,amount,paid) values(" + str(b) + "," + str(
            s) + ",str_to_date('" + d + "','%d-%b-%y')," + str(a) + ",0);"
        cur.execute(sql)
        con.commit()
        self.crnumber.set(0)
        self.cramount.set(0)
        self.showcredits()

if __name__ == "__main__":
    a = CreditNote()
    a.mainloop()
