from tkinter import *
import connectdb as cdb
import comp
import tkinter.messagebox as tkMessageBox
import printer as printbill
import shelve
import datetime as dt


class Cancel(Frame):

    def __init__(self, master=None, parent=None, *arg, **karg):
        if not parent:
            parent = Toplevel()
        Frame.__init__(self, parent, *arg, **karg)
        self.master = master
        self.parent = parent
        self.pack()
        parent.title("Cancel Bill")
        f1 = Frame(self)  #search frame
        f1.pack(side=TOP, padx=15, pady=10, ipadx=20, ipady=10)
        Label(f1, text="Bill Number").pack(side=LEFT)
        self.billno = IntVar()
        self.billno.set("")
        t = comp.NumEntry(f1, textvariable=self.billno)
        t.pack(side=LEFT, padx=5)
        t.bind("<Return>", self.searchbill)
        b = Button(f1, text="Search", command=self.searchbill)
        b.pack(side=LEFT, padx=5)
        b.bind("<Return>", self.searchbill)

        f2 = Frame(self)  #bill details
        f2.pack(side=TOP, fill=BOTH, expand=1, padx=10)
        sb = Scrollbar(f2)
        sb.pack(side=RIGHT, fill=Y)
        self.canvas = Canvas(f2, bd=1, relief=SUNKEN, yscrollcommand=sb.set, width=300, height=300)
        self.canvas.pack(fill=BOTH, expand=1)
        sb.config(command=self.canvas.yview)

        f3 = Frame(self)
        f3.pack(side=TOP, ipadx=20, ipady=10)
        self.cancelbutton = Button(f3, text="cancel Bill", state=DISABLED, command=self.cancelbill)
        self.cancelbutton.pack(side=LEFT, padx=20, pady=10)
        self.updatebutton = Button(f3, text="update Bill", command=self.updatebill, state=DISABLED)
        self.updatebutton.pack(side=LEFT, padx=20, pady=10)
        self.reprintbutton = Button(f3, text="Reprint Bill", command=self.reprint, state=DISABLED)
        self.reprintbutton.pack(side=LEFT, pady=10)

    def searchbill(self, event=None):
        self.curbill = self.billno.get()
        self.canvas.delete(ALL)
        self.items = []
        db = cdb.Db().connection()
        cur = db.cursor(cdb.dictcursor)
        sql = ("select drug.name,sale.id,sale.count,stock.price,stock.discount,stock.cgstp,stock.sgstp,bill.name as "
               "patient,bill.net as total,bill.date from bill join sale on bill.id=sale.bill join stock on "
               "sale.stock=stock.id join drug on stock.drug_id=drug.id where bill.id={};").format(str(self.curbill))
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) == 0:
            return
        row = rows[0]
        f = Frame(self.canvas)
        Label(f, text=row['patient']).pack(side=LEFT, padx=10, pady=10)
        Label(f, text=row['date']).pack(side=LEFT, padx=10, pady=10)
        Label(f, text=row['total']).pack(side=LEFT, padx=10, pady=10)
        self.canvas.create_window(1, 1, window=f, anchor=NW)
        i = 1
        for row in rows:
            f = Frame(self.canvas)
            Label(f, text=row['name'], width=20).pack(side=LEFT, padx=10, pady=10)
            f.drug = row['name']
            f.oldcount = row['count']
            f.count = IntVar()
            f.count.set(f.oldcount)
            comp.NumEntry(f, textvariable=f.count, width=5).pack(side=LEFT, padx=10, pady=10)
            f.id = row['id']
            f.price = row['price'] * (1 - row['discount'] / 100) * (1 + row['cgstp'] / 100 + row['sgstp'] / 100)
            self.canvas.create_window(1, 1 + i * 40, window=f, anchor=NW)
            i = i + 1
            self.items.append(f)
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))
        self.cancelbutton.config(state=NORMAL)
        self.updatebutton.config(state=NORMAL)
        self.reprintbutton.configure(state=NORMAL)

    def updatebill(self):
        if not tkMessageBox.askyesno("confirm update", "Are you sure you want to modify bill " + str(self.curbill),
                                     parent=self.parent):
            return
        self.billno.set(self.curbill)
        con = cdb.Db().connection()
        cur = con.cursor()
        returnamount = 0
        dat = dt.date.today()
        dat = "      {:%d %b %y, %a}".format(dat)
        printout = []
        printout.extend(printbill.header)
        printout.extend(("", "    BILL RETURN ", "Bill number: " + str(self.curbill), dat, ""))
        ip = False
        if self.isip(self.curbill, cur):
            ip = True
        try:
            for f in self.items:
                count = f.count.get()
                if count != f.oldcount:
                    if count >= f.oldcount or self.isexpired(f.id, cur):
                        printout.append(
                            "cant return " + f.drug + " since either count entered is wrong, or the stock is expired")
                        continue
                    sql = "update sale set count = {} where id={}".format(str(count), str(f.id))
                    cur.execute(sql)
                    returnamount = returnamount + (f.oldcount - count) * f.price
                    printout.append(
                        f.drug + "   " + str(f.oldcount - count) + "     " + str((f.oldcount - count) * f.price))
                    sql = ("update stock set cur_count=cur_count+{} where stock.id = (select stock from sale where "
                           "id={});").format(str(f.oldcount - count), str(f.id))
                    cur.execute(sql)

            if returnamount > 0:
                sql = "update bill set net = net-{} where id={};".format(str(returnamount), str(self.curbill))
                cur.execute(sql)
                printout.extend(("", " RETURN AMOUNT:   " + str(returnamount)))
            con.commit()
            self.master.restock()
            if not ip:
                printbill.printinfo(printout)
                self.reprint()
                sh = shelve.open("data")
                try:
                    billreturn = sh['return']
                except:
                    billreturn = 0
                try:
                    bills = sh["bills"]
                except:
                    sh['bills'] = {"sale": [], "ipsale": []}
                sh['return'] = float(billreturn) + float(returnamount)
                myar = sh['bills']
                myar['sale'].append([self.curbill, -(returnamount)])
                sh['bills'] = myar
                sh.close()
            else:
                tkMessageBox.showinfo("Bill Updated", "bill print out only if not IP bill", parent=self.parent)

        except cdb.mdb.Error as e:
            tkMessageBox.showerror("Error " + str(e.args[0]), e.args[1], parent=self.parent)
            con.rollback()
        finally:
            con.close()
            self.searchbill()

    def cancelbill(self):
        if not tkMessageBox.askyesno("confirm Cancel", "Are you sure you want to cancel bill " + str(self.curbill),
                                     parent=self.parent):
            return
        self.billno.set(self.curbill)
        con = cdb.Db().connection()
        cur = con.cursor()
        sql = ("select sale.id from sale join bill on sale.bill=bill.id join stock on sale.stock=stock.id where "
               "stock.expiry < curdate() + interval 30 day and bill.id= %s;")
        cur.execute(sql, [str(self.curbill)])
        if cur.rowcount > 0:
            tkMessageBox.showerror("Can not cancel bill", "looks like one of the item is near expiry",
                                   parent=self.parent)
            return
        try:
            ip = False
            if self.isip(self.curbill, cur):
                ip = True
            sql = "select sale.id as saleid, sale.count as count,sale.stock as stock from sale where sale.bill=%s;"
            cur.execute(sql, [self.curbill])
            rows = cur.fetchall()
            for row in rows:
                sql = "update stock set cur_count=cur_count+{} where stock.id={}".format(row[1], row[2])
                cur.execute(sql)
                sql = "update sale set count=0 where id={}".format(row[0])
                cur.execute(sql)
            sql = "select net from bill where id={};".format(self.curbill)
            cur.execute(sql)
            row = cur.fetchone()
            returnamount = row[0]
            sql = "update bill set net=0 where id={};".format(self.curbill)
            cur.execute(sql)
            con.commit()
            self.master.restock()
            if not ip:
                printout = []
                printout.extend(printbill.header)
                dat = dt.date.today()
                dat = "      {:%d %b %y, %a}".format(dat)
                printout.extend(("", "    BILL CANCEL", dat))
                printout.extend(("Bill no:" + str(self.curbill), "", "Refund amount  " + str(returnamount)))
                printbill.printinfo(printout)
                sh = shelve.open("data")
                try:
                    billreturn = sh['return']
                except:
                    billreturn = 0
                sh['return'] = float(billreturn) + float(returnamount)
                myar = sh['bills']
                myar['sale'].append([self.curbill, -(returnamount)])
                sh['bills'] = myar
                sh.close()
            else:
                tkMessageBox.showinfo("Bill Cancelled", "Refund only if bill is not IP", parent=self.parent)

        except cdb.mdb.Error as e:
            tkMessageBox.showerror("Error " + str(e.args[0]), e.args[1], parent=self.parent)
            con.rollback()
        finally:
            con.close()
            self.searchbill()

    def isexpired(self, sale, cur):
        sql = (
            "select stock.id from sale join stock on sale.stock=stock.id where stock.expiry>curdate()+interval 30 day "
            "and sale.id= {};").format(sale)
        cur.execute(sql)
        if cur.rowcount > 0:
            return False
        else:
            return True

    def isip(self, bill, cur):
        sql = ("select patient.id from patient join credit on patient.id=credit.patientid join bill on "
               "credit.billid=bill.id where patient.discharged=0 and bill.id={};").format(bill)
        cur.execute(sql)
        if cur.rowcount > 0:
            return True
        else:
            return False

    def reprint(self, cur=None, biller=None):
        billno = self.curbill
        if not cur:
            cur = cdb.Db().connection().cursor(cdb.dictcursor)
        if not biller:
            sql = ("select bill.name as patient, doc.name as doc,bill.date as date, bill.net as net,bill.cgst as cgst,"
                   "bill.sgst as sgst, drug.name as drug, manufacture.name as manufacture, sale.count as qty,"
                   "stock.batch as batch,stock.expiry as expiry,stock.price as price, stock.cgstp as cgstp, "
                   "stock.sgstp as sgstp,stock.discount as discount,bill.cgst as cgst,bill.sgst as sgst from bill "
                   "join sale on sale.bill=bill.id join stock on sale.stock=stock.id join drug on "
                   "stock.drug_id=drug.id left join manufacture on manufacture.id=drug.manufacture left join doc on "
                   "bill.doc=doc.id where bill.id={};").format(billno)
            cur.execute(sql)
            r = cur.fetchone()
            patient = r["patient"]
            doc = r["doc"]
            date = r["date"]
            total = r["net"] - r["cgst"] - r["sgst"]
            cgst = r["cgst"]
            sgst = r["sgst"]
            cur.scroll(0, mode="absolute")
            rows = cur.fetchall()
            items = []
            for r in rows:
                price = float(r['price']) - float(r['price']) * float(r['discount']) / 100
                item = (r["drug"], r["manufacture"], r['batch'], r['qty'], r['expiry'], price * r['qty'])
                items.append(item)
            sql = ("select patient.name from bill join credit on bill.id=credit.billid join patient on "
                   "credit.patientid=patient.id where bill.id={} and patient.discharged=0;").format(
                billno)
            ip = None
            cur.execute(sql)
            if cur.rowcount > 0:
                r = cur.fetchone()
                f = r["name"].split("::")
                ip = f[0]
            biller = {"billno": str(billno) + "  COPY", "patient": patient, "doc": doc, "date": date, "total": total,
                      "items": items, "ip": ip, "cgst": cgst, "sgst": sgst}
        printbill.printbill(biller['billno'], biller['patient'], biller['doc'], biller['date'], biller['total'],
                            biller['cgst'], biller['sgst'], biller['items'], ip=biller['ip'])


if __name__ == "__main__":
    f = Cancel(Tk())
    f.mainloop()
