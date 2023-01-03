import tkinter as tk
from time import sleep
import mysql.connector as conn
from tkinter import messagebox 
import os
import csv
import requests
import pickle
import base64
from datetime import date
import customtkinter as ck
import hashlib
from tkinter import filedialog as fd
from os.path import exists


class main:
    def __init__(self) -> None:
        ck.set_appearance_mode("dark")
        ck.set_default_color_theme("blue")

        self.mysql_password = ''
        self.mysql_username = ''
        self.db = ''
        self.cursor = ''
        
        self.root = ck.CTk()
        self.root.title("Library Management System (APS New Cantt, Prayagraj)")
        self.root.bind("<Key>", lambda key: self.listener(key,self.root))
        self.root.withdraw()
        
        self.win_del = ck.CTk()
        self.win_del.title("Delete Books")
        self.win_del.bind("<Key>", lambda key: self.listener(key,self.win_del))
        self.win_del.withdraw()

        self.win_add = ck.CTk()
        self.win_add.title("Add Books")
        self.win_add.bind("<Key>", lambda key: self.listener(key,self.win_add))
        self.win_add.withdraw()
        
        self.win_return = ck.CTk()
        self.win_return.title("Return Books")
        self.win_return.bind("<Key>", lambda key: self.listener(key,self.win_return))
        self.win_return.withdraw()
 
        self.issue = ck.CTk()
        self.issue.title("Issue Books")
        self.issue.bind("<Key>", lambda key: self.listener(key,self.issue))
        self.issue.withdraw()
        
        self.reset = ck.CTk()
        self.reset.title("Reset Password")
        self.reset.bind("<Key>", lambda key: self.listener(key,self.reset))
        self.reset.withdraw()
        
        self.fine = 50
        self.fields = ["BOOK_ID",'BOOK_NAME','AUTHOR_NAME','BOOK_PRICE','QTY']


    # -----------------------------------------MAIN FUNCTIONS-----------------------------------------
    
    def listener(self, key, window):
        win_title = str(window.wm_title())

        if key.keysym == "F11":
            if window.wm_attributes()[7] == 0:
                window.attributes("-fullscreen", True)
            else:
                window.attributes("-fullscreen", False)

        elif key.keysym == "F1":
            self.reset_fine_gui()

        elif key.keysym == "F2":
            self.reset_password_gui()
        
        elif key.keysym == "F3":
            if window.appearance_mode == 1:
                window.set_appearance_mode("light")
            else:
                window.set_appearance_mode("dark")

        elif key.keysym == "F5":
            self.add_books_csv()


    def on_closing(self):
        confirm = messagebox.askquestion("Confirm", "Do you really want to quit?")
        if confirm.lower() == "yes":
            exit()

    def win_issue_on_closing(self):
        self.issue.withdraw()

    def reset_on_closing(self):
        self.reset.withdraw()
    
    def reset_fine_on_closing(self):
        self.reset_fine.withdraw()

    def win_return_on_closing(self):
        self.win_return.withdraw()

    def win_del_on_closing(self):
        self.win_del.withdraw()

    def win_add_on_closing(self):
        self.win_add.withdraw()
    
    def abt_on_closing(self):
        self.about.withdraw()
    
    def login_on_closing(self):
        exit()

    def add_books(self, book_id, book_name, author, bookprice, qty):
        sql = 'INSERT INTO BOOKS(BOOK_ID, BOOK_NAME, AUTHOR_NAME, BOOK_PRICE, QTY) VALUES(%s, %s, %s, %s, %s)'
        val = (book_id.get(), book_name.get(), author.get(), bookprice.get(), qty.get())
        
        try:
            self.cursor.execute(sql, val)
            self.db.commit()
            messagebox.showinfo("Success", "Book added successfully!")
        except:
            messagebox.showerror("Error", "Something Went Wrong!")

    def delete_book(self, del_book_id):
        try:
            self.cursor.execute('delete from books where BOOK_ID=' + del_book_id.get())
            self.db.commit()
            messagebox.showinfo("Success", 'Book deleted successfully!')
        except:
            messagebox.showerror("Error", "Something Went Wrong!")

    def issue_books(self, std_name, class_, section, roll, issue_bid, issue_date):
        self.cursor.execute("SELECT QTY FROM BOOKS WHERE BOOK_ID="+issue_bid.get())
        result = self.cursor.fetchall()
        if (len(result) != 0) and (result[0][-1] != 0):
            self.cursor.execute("select STUDENT_ID from ISSUED_BOOKS;")

            try:
                std_id = self.cursor.fetchall()[-1][0]                
            except:
                std_id = 0

            try:
                self.cursor.execute("SELECT BOOK_PRICE FROM BOOKS WHERE BOOK_ID="+issue_bid.get())
                bprice = self.cursor.fetchall()[0][0]
            except IndexError:
                messagebox.showerror("Error", "Book Not Available. Check the list of books again.")

            try:
                sql = 'INSERT INTO ISSUED_BOOKS(STUDENT_ID, STUDENT_NAME, CLASS, SECTION, ROLL_NO, BOOK_ID, BOOK_PRICE, ISSUE_DATE) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
                val = ((std_id+1), std_name.get(), class_.get().upper(), section.get().upper(), int(roll.get()), int(issue_bid.get()), int(bprice), issue_date.get())
                
                self.cursor.execute(sql, val)
                self.db.commit()

                self.cursor.execute("UPDATE BOOKS SET QTY=QTY-1 WHERE BOOK_ID="+issue_bid.get())
                self.db.commit()

                messagebox.showinfo("Success", "Book Issued Successfully!")
            except:
                messagebox.showerror("Error", "Something went wrong.")

        else:
            messagebox.showinfo("Info", "Sorry, the book is not currently available!")

    def return_books(self, return_date, return_stdid):
        try:
            return_date_splitted = return_date.get().split('-')
            date1 = date(int(return_date_splitted[0]), int(return_date_splitted[1]), int(return_date_splitted[2]))
            
            self.cursor.execute("SELECT * FROM ISSUED_BOOKS")
            rows = self.cursor.fetchall()
            
            for i in rows:
                if int(i[0]) == int(return_stdid.get()):
                    date2 = i[7]

            days = (date1 - date2).days
            if days > 7:
                self.cursor.execute("UPDATE ISSUED_BOOKS SET FINE=%s WHERE STUDENT_ID=%s", ((days-7)*self.fine, return_stdid.get()))
                self.db.commit()

            self.cursor.execute("SELECT BOOK_ID FROM ISSUED_BOOKS WHERE STUDENT_ID="+return_stdid.get())
            return_bid = self.cursor.fetchall()[-1][0]

            self.cursor.execute("UPDATE ISSUED_BOOKS SET RETURN_DATE=%s WHERE STUDENT_ID=%s", (return_date.get(), return_stdid.get()))
            self.db.commit()

            self.cursor.execute("UPDATE BOOKS SET QTY=QTY+1 WHERE BOOK_ID="+str(return_bid))
            self.db.commit()

            messagebox.showinfo("Info", "Success!")

        except Exception as e:
            messagebox.showerror("Error", f"Something Went Wrong!\n{e}")

    
    def view_books(self):
        self.cursor.execute("DESC BOOKS")
        fields = []

        for i in self.cursor.fetchall():
            fields.append(i[0])
        
        self.cursor.execute("SELECT * FROM BOOKS")
        rows = self.cursor.fetchall()

        filepath = fd.asksaveasfilename(title="Save as")

        try:
            with open(filepath, 'w') as file:
                writer = csv.writer(file)
                writer.writerow(fields)
                writer.writerows(rows)

            messagebox.showinfo(title="Successfull", message="CSV file has been successfully created!")

            sleep(1)
            os.startfile(filepath)
        except:
            messagebox.showerror("Error", "Something Went Wrong!")

    def view_issued_books(self):
        self.cursor.execute('DESC ISSUED_BOOKS')
        fields = []

        for i in self.cursor.fetchall():
            fields.append(i[0])

        self.cursor.execute("SELECT * FROM ISSUED_BOOKS")
        rows = self.cursor.fetchall()

        try:
            path = fd.asksaveasfile().name
        except:
            messagebox.showerror("Error","Please try to save the file with different name (if it is running in background)!")
   
        try:
            with open(path, 'w') as file:
                writer = csv.writer(file)
                writer.writerow(fields)
                writer.writerows(rows)

            messagebox.showinfo(title="Successfull", message="CSV file made!!")
            sleep(1)
            os.startfile(path)

        except:
            messagebox.showerror("Error", "Something Went Wrong!")

    def reset_password(self, new_passwrd, username, old_passwrd):
        self.cursor.execute("SELECT * FROM LIB_USERS")
        query1 = self.cursor.fetchall()[0]
        new_passwrd_hash = hashlib.sha256(new_passwrd.encode()).hexdigest()
        old_passwrd_hash = hashlib.sha256(old_passwrd.encode()).hexdigest()

        try:
            self.cursor.execute("UPDATE LIB_USERS SET PASSWORD=%s WHERE USERNAME=%s AND PASSWORD=%s", (new_passwrd_hash,username,old_passwrd_hash))
            self.db.commit()
        except:
            messagebox.showerror("Error", "Something went wrong.")
        
        self.cursor.execute("SELECT * FROM LIB_USERS")
        query2 = self.cursor.fetchall()[0]
        
        if new_passwrd_hash == old_passwrd_hash:
            messagebox.showinfo("Info", "Old Password and New Password are same!")

        elif query1 == query2:
            messagebox.showerror("Error", "Username or Old Password is/are incorrect.")
        
        else:
            messagebox.showinfo("Info", "Password Changed Successfully.")

    def add_books_csv(self):
        with open("csv_books.csv","r") as file:
            reader = csv.reader(file)
            fields = next(reader)
            data = [i for i in reader]

            if data == []:
                messagebox.showinfo('Info","Please enter some data in "csv_books.csv file!"')
    
            elif data[0][0] == 'BOOK_ID':
                messagebox.showinfo("Info","Please enter column names in the very first row of the csv file!")
            
            else:
                try:
                    for i in data:
                        self.cursor.execute("INSERT INTO BOOKS VALUES(%s, %s, %s, %s, %s)",(i[0],i[1],i[2],i[3],i[4]))
                        self.db.commit()
                    messagebox.showinfo("Success","Data inserted successfully!!")

                except:
                    messagebox.showerror("Error","Something went wrong!")
    

    # -----------------------------------------MAIN FUNCTIONS END--------------------------------



    # -----------------------------------------GUI START-----------------------------------------

    def main_window(self):
        self.root.deiconify()
        self.root.state("zoomed")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        menu = tk.Menu(self.root)
         
        help = tk.Menu(menu, tearoff = 0)
        menu.add_cascade(label ='Help', menu = help)
        help.add_command(label ='Change Fine Amount    F1', command = self.reset_fine_gui)
        help.add_command(label ='Reset Password        F2', command = self.reset_password_gui)
        help.add_command(label="Add Books (via csv) F5", command=self.add_books_csv)

        ck.CTkLabel(self.root, text="Welcome", text_font=("Roboto",25)).place(relx=0.25, rely=0.1, relheight=0.1, relwidth=0.5) 

        add_btn = ck.CTkButton(self.root, text_font=("Roboto",16), text="Add Book", command=self.add_books_gui)
        add_btn.place(relx=0.28, rely=0.26, relwidth=0.45, relheight=0.1)

        delete_btn = ck.CTkButton(self.root, text_font=("Roboto",16), text="Delete Book", command=self.delete_book_gui)
        delete_btn.place(relx=0.28, rely=0.38, relwidth=0.45, relheight=0.1)
            
        view_btn = ck.CTkButton(self.root, text_font=("Roboto",16), text="Download List of Books", command=self.view_books)
        view_btn.place(relx=0.28, rely=0.50, relwidth=0.45, relheight=0.1)
            
        issue_btn = ck.CTkButton(self.root, text_font=("Roboto",16), text="Issue Book to Student", command=self.issue_books_gui)
        issue_btn.place(relx=0.28, rely=0.62, relwidth=0.45, relheight=0.1)
            
        return_btn = ck.CTkButton(self.root, text_font=("Roboto",16), text="Return Book", command=self.return_books_gui)
        return_btn.place(relx=0.28, rely=0.74, relwidth=0.45, relheight=0.1)
        
        view_issued = ck.CTkButton(self.root, text_font=("Roboto",16), text="View Issued Books", command=self.view_issued_books)
        view_issued.place(relx=0.28, rely=0.86, relwidth=0.45, relheight=0.1)

        self.root.config(menu = menu)
        self.root.mainloop()

    def add_books_gui(self):
        self.win_add.protocol("WM_DELETE_WINDOW", self.win_add_on_closing)

        self.win_add.deiconify()
        self.win_add.state("zoomed")

        ck.CTkLabel(self.win_add, text="Add Books", text_font=("Roboto",30)).place(relx=0.21, rely=0.1, relheight=0.1, relwidth=0.6) 

        add_frame = ck.CTkFrame(self.win_add, bg='black')
        add_frame.place(relx=0.27, rely=0.4, relheight=0.5, relwidth=0.5)

        ck.CTkLabel(add_frame, text="Book ID:", text_font=("Roboto",18)).place(relx=0.05, rely=0.03)

        book_id = ck.CTkEntry(add_frame, width=480, text_font=("Roboto",18))
        book_id.place(relx=0.3, rely=0.03)

        ck.CTkLabel(add_frame, text="Book Name:", text_font=("Roboto",18)).place(relx=0.05, rely=0.16)

        book_name = ck.CTkEntry(add_frame, width=480, text_font=("Roboto",18))
        book_name.place(relx=0.3, rely=0.16)

        ck.CTkLabel(add_frame, text="Author Name:", text_font=("Roboto",18)).place(relx=0.05, rely=0.29)

        author = ck.CTkEntry(add_frame, width=480, text_font=("Roboto",18))
        author.place(relx=0.3, rely=0.29)

        ck.CTkLabel(add_frame, text="Book Price:", text_font=("Roboto",18)).place(relx=0.05, rely=0.42)

        bookprice = ck.CTkEntry(add_frame, width=480, text_font=("Roboto",18))
        bookprice.place(relx=0.3, rely=0.42)

        ck.CTkLabel(add_frame, text="Book Qty:", text_font=("Roboto",18)).place(relx=0.05, rely=0.55)

        qty = ck.CTkEntry(add_frame, width=480, text_font=("Roboto",18))
        qty.place(relx=0.3, rely=0.55)

        submit = ck.CTkButton(add_frame, text="Submit", text_font=("Roboto",18), command=lambda: self.add_books(book_id, book_name, author, bookprice, qty))
        submit.place(relx=0.40, rely=0.75, relwidth=0.4)
        
        self.win_add.mainloop()


    def delete_book_gui(self):
        self.win_del.protocol("WM_DELETE_WINDOW", self.win_del_on_closing)

        self.win_del.deiconify()
        self.win_del.state("zoomed")
        
        ck.CTkLabel(self.win_del, text="Delete Books", text_font=("Roboto",30)).place(relx=0.21, rely=0.1, relheight=0.1, relwidth=0.6)

        del_frame = ck.CTkFrame(self.win_del, bg='black')
        del_frame.place(relx=0.27, rely=0.4, relheight=0.5, relwidth=0.5)

        ck.CTkLabel(del_frame, text="Book ID:", text_font=("Roboto",18)).place(relx=0.1, rely=0.4)

        del_book_id = ck.CTkEntry(del_frame, width=400, text_font=("Roboto",18))
        del_book_id.place(relx=0.36, rely=0.4)

        submit = ck.CTkButton(del_frame, text="Submit", text_font=("Roboto",18), command=lambda: self.delete_book(del_book_id))
        submit.place(relx=0.3,rely=0.75, relwidth=0.5)

        self.win_del.mainloop()

    
    def issue_books_gui(self):
        self.issue.protocol("WM_DELETE_WINDOW", self.win_issue_on_closing)
        self.issue.deiconify()
        self.issue.state("zoomed")

        issue_frame = ck.CTkFrame(self.issue)
        issue_frame.place(relx=0.16, rely=0.28, relheight=0.65, relwidth=0.7)
        
        ck.CTkLabel(self.issue, text="Issue Books", text_font=("Roboto",25)).place(relx=0.21, rely=0.1, relheight=0.1, relwidth=0.6)
        ck.CTkLabel(issue_frame, text="Student Name -", text_font=("Roboto",18)).place(relx=0.05, rely=0.07)

        std_name = ck.CTkEntry(issue_frame, width=480, text_font=("Roboto",18))
        std_name.place(relx=0.43, rely=0.07)

        ck.CTkLabel(issue_frame, text="Class -", text_font=("Roboto",20)).place(relx=0.05, rely=0.18)

        class_ = ck.CTkEntry(issue_frame, width=480, text_font=("Roboto",18))
        class_.place(relx=0.43, rely=0.18)

        ck.CTkLabel(issue_frame, text="Section -", text_font=("Roboto",18)).place(relx=0.05, rely=0.31)

        section = ck.CTkEntry(issue_frame, width=480, text_font=("Roboto",18))
        section.place(relx=0.43, rely=0.31)

        ck.CTkLabel(issue_frame, text="Roll Number -", text_font=("Roboto",18)).place(relx=0.05, rely=0.44)    

        roll = ck.CTkEntry(issue_frame, width=480, text_font=("Roboto",18))
        roll.place(relx=0.43, rely=0.44)

        ck.CTkLabel(issue_frame, text="Book ID -", text_font=("Roboto",18)).place(relx=0.05, rely=0.57)

        issue_bid = ck.CTkEntry(issue_frame, width=480, text_font=("Roboto",18))
        issue_bid.place(relx=0.43, rely=0.57)

        ck.CTkLabel(issue_frame, text="Issue Date (YYYY-MM-DD) -", text_font=("Roboto",18)).place(relx=0.05, rely=0.70)
        
        issue_date = ck.CTkEntry(issue_frame, width=480, text_font=("Roboto",18))
        issue_date.place(relx=0.43, rely=0.70)

        submit = ck.CTkButton(issue_frame, text="Submit", text_font=("Roboto",18), command=lambda: self.issue_books(std_name, class_, section, roll, issue_bid, issue_date))
        submit.place(relx=0.3, rely=0.85, relwidth=0.5)
    
        self.issue.mainloop()

    def return_books_gui(self):
        self.win_return.protocol("WM_DELETE_WINDOW", self.win_return_on_closing)
        self.win_return.deiconify()
        self.win_return.state("zoomed")
        
        return_frame = ck.CTkFrame(self.win_return, bg='black')
        return_frame.place(relx=0.16, rely=0.28, relheight=0.65, relwidth=0.7)

        ck.CTkLabel(self.win_return, text="Return Books", text_font=("Roboto",25)).place(relx=0.21, rely=0.1, relheight=0.1, relwidth=0.6)

        ck.CTkLabel(return_frame, bg='black', fg='lime', text="Student ID -", text_font=("Roboto",20)).place(relx=0.05, rely=0.35)
        
        return_stdid = ck.CTkEntry(return_frame, width=480, text_font=("Roboto",18))
        return_stdid.place(relx=0.37, rely=0.35)

        ck.CTkLabel(return_frame, text="Return Date -", text_font=("Roboto",20)).place(relx=0.05, rely=0.48)

        return_date = ck.CTkEntry(return_frame, width=480, text_font=("Roboto",18))
        return_date.place(relx=0.37, rely=0.48)

        submit = ck.CTkButton(return_frame, text="Submit", text_font=("Roboto",22), command=lambda: self.return_books(return_date, return_stdid))
        submit.place(relx=0.3, rely=0.8, relwidth=0.5)

        self.win_return.mainloop()

    def reset_fine_gui(self):
        my_fine = ck.CTkInputDialog(self.root, title="Fine", text="Enter your desired fine.")
        my_fine = my_fine.get_input()

        try:
            self.fine = int(my_fine)
            messagebox.showinfo("Info","Fine Updated Successfully!")
            with open("info.dat",'wb') as file:
                data = {"username":self.mysql_username,"password":self.mysql_password,"fine":self.fine}
                data = f'hafhahgha[adauhaicnacb[]a[afag=+{str(data)}+ajkfhacuagugxuabjrbjakajajda=-=-===[]agag'.encode("ascii")
                data = base64.b64encode(data)
                pickle.dump(data,file)
        except:
            messagebox.showerror("Error", "Something went wrong!")

    def reset_password_gui(self):
        self.reset.protocol("WM_DELETE_WINDOW", self.reset_on_closing)
        self.reset.deiconify()
        self.reset.state("zoomed")

        ck.CTkLabel(self.reset, text="Reset Password", text_font=("Roboto",25)).place(relx=0.45, rely=0.1)

        ck.CTkLabel(self.reset, text="Username: ", text_font=("Roboto",20)).place(relx=0.26, rely=0.35)
        username = ck.CTkEntry(self.reset, width=480)
        username.place(relx=0.43, rely=0.35)

        ck.CTkLabel(self.reset, text="Old Password: ", text_font=("Roboto",20),).place(relx=0.26, rely=0.45)
        
        old_passwrd = ck.CTkEntry(self.reset, width=480, show="*")
        old_passwrd.place(relx=0.43, rely=0.45)

        hide_var1 = ck.StringVar(value="on")

        def switch_event1():
            if hide_var1.get() == "on":
                old_passwrd.configure(show = "*")
            else:
                old_passwrd.configure(show = "")

        hide_switch = ck.CTkSwitch(master=self.reset, text="Hide Password", command=switch_event1,
                                        variable=hide_var1, onvalue="on", offvalue="off", text_font=("Roboto",13))
        hide_switch.place(relx=0.76, rely=0.46)


        ck.CTkLabel(self.reset, text="New Password: ", text_font=("Roboto",20)).place(relx=0.26, rely=0.55)
        new_passwrd = ck.CTkEntry(self.reset, width=480, show="*")
        new_passwrd.place(relx=0.43,rely=0.55)

        hide_var2 = ck.StringVar(value="on")

        def switch_event2():
            if hide_var2.get() == "on":
                new_passwrd.configure(show = "*")
            else:
                new_passwrd.configure(show = "")

        hide_switch2 = ck.CTkSwitch(master=self.reset, text="Hide Password", command=switch_event2,
                                        variable=hide_var2, onvalue="on", offvalue="off", text_font=("Roboto",13))
        hide_switch2.place(relx=0.76, rely=0.55)


        reset_btn = ck.CTkButton(self.reset, text="Submit", width=240, text_font=("Roboto",18), command=lambda: self.reset_password(new_passwrd.get(), username.get(), old_passwrd.get()))
        reset_btn.place(relx=0.46, rely=0.7)

        self.reset.mainloop()

    def load(self):        
        ck.set_appearance_mode("dark")

        load = ck.CTk()
        load.title("Loading")
        load.attributes("-fullscreen",True)
        load.config(bg = "black")

        ck.CTkLabel(load, text="Army Public School, New Cantt", text_font=("Courier New",25), text_color="lime").place(relx=0.3, rely=0.05)
        ck.CTkLabel(load, text="Prayagraj", text_font=("Courier New",25), text_color="lime").place(relx=0.42, rely=0.11)
        ck.CTkLabel(load, text="Library Management System", text_font=("Courier New",25), text_color="lime").place(relx=0.32, rely=0.17)
        ck.CTkLabel(load, text="Loading...", text_font=("Courier New",25), text_color="lime").place(relx=0.17, rely=0.43)

        box = 0.15
        for i in range(35):
            ck.CTkLabel(load, text="", bg_color='black', height=20, width=20).place(relx=(box)+0.02, rely=0.5)
            box += 0.02 

        for i in range(3):
            box = 0.15
            for j in range(35):
                ck.CTkLabel(load, text="", bg_color="lime", height=20, width=20).place(relx=(box)+0.02, rely=0.5)
                sleep(0.02)
                box += 0.02
                load.update()
            box = 0.15
            
            for j in range(35):
                ck.CTkLabel(load, text="", bg_color='black', height=20, width=20).place(relx=(box)+0.02, rely=0.5)
                sleep(0.02)
                box += 0.02
                load.update()
        load.destroy()


    def check_creds(self, screen, username, passwrd):
        try:
            self.db = conn.connect(host='localhost', user=self.mysql_username, password=self.mysql_password, database='library')
            self.cursor = self.db.cursor()
        except conn.Error:
            reply = messagebox.askyesno("Error","Incorrect MySQL Username/Password!!\nDo you want to update your MySQL credentials?")
            if reply:
                self.start()
            else:
                exit()

        self.cursor.execute("SELECT * FROM lib_users")
        result = self.cursor.fetchall()[0]
        passwrd_hash = hashlib.sha256(passwrd.get().encode()).hexdigest()

        if (result[0] == username.get()) and (result[1] == passwrd_hash):
            screen.destroy()
            self.load()
            self.main_window()
        else:
            messagebox.showerror("Error", "Invalid Credentials.")


    def login(self):
        login_screen =ck.CTk()
        login_screen.title("Login")
        login_screen.geometry("950x400")
        login_screen.resizable(False,False)
        login_screen.protocol("WM_DELETE_WINDOW", self.login_on_closing)


        ck.CTkLabel(login_screen, text="Login", text_font=("Roboto",22,'bold')).place(relx=0.45, rely=0.05)
        ck.CTkLabel(login_screen, text="Username:", text_font=("Roboto",18)).place(relx=0.15, rely=0.3)

        username = ck.CTkEntry(login_screen, width=360)
        username.place(relx=0.35, rely=0.3)

        ck.CTkLabel(login_screen, text="Password:", text_font=("Roboto",18)).place(relx=0.15, rely=0.6)
        passwrd = ck.CTkEntry(login_screen, width=360, show="*")
        passwrd.place(relx=0.35, rely=0.6)

        hide_var = ck.StringVar(value="on")

        def switch_event():
            if hide_var.get() == "on":
                passwrd.configure(show = "*")
            else:
                passwrd.configure(show = "")

        hide_switch = ck.CTkSwitch(master=login_screen, text="Hide Password", command=switch_event,
                                        variable=hide_var, onvalue="on", offvalue="off", text_font=("Roboto",13))
        hide_switch.place(relx=0.75, rely=0.61)

        submit = ck.CTkButton(login_screen, text="Submit", text_font=("Roboto",12), command=lambda: self.check_creds(login_screen, username, passwrd))
        submit.place(relx=0.45, rely=0.8)

        login_screen.mainloop()

    def start(self):
        my_user = ck.CTkInputDialog(self.root, title="Username", text="Enter your mysql username.")
        my_user = my_user.get_input()
    
        my_pass = ck.CTkInputDialog(self.root, title="Password", text="Enter your mysql password.")
        my_pass = my_pass.get_input()

        fine = ck.CTkInputDialog(self.root, title="Fine", text="Enter desired fine amount.")
        fine = fine.get_input()

        try:
            self.db = conn.connect(host='localhost', user=my_user, password=my_pass, db='library')
            self.cursor = self.db.cursor()

            self.mysql_password = my_pass
            self.mysql_username = my_user

            with open("info.dat",'wb') as file:
                data = {"username":my_user,"password":my_pass,"fine":fine}
                data = f'hafhahgha[adauhaicnacb[]a[afag=+{str(data)}+ajkfhacuagugxuabjrbjakajajda=-=-===[]agag'.encode("ascii")
                data = base64.b64encode(data)
                pickle.dump(data,file)
        except:
            messagebox.showerror("Error","Something went wrong!!\nTry Checking your MySQL Credentials!")
        
        self.login()

    # -----------------------------------------------GUI END-----------------------------------------------

current_version = 'v1.0'


response = requests.get("https://api.github.com/repos/mymadhavyadav07/Library-Management-System/releases/latest")
try:
    reply = response.json()['message']
    if reply == "Not Found":
        print("No version available")
except KeyError:
    version = response.json()['name']
    repo_url = f"https://github.com/mymadhavyadav07/Library-Management-System/archive/refs/tags/{version}.zip"
    
    if current_version < version:
        reply = messagebox.askyesno("Info","New version is available.\nDo you want an update??")
        if reply:
            r = requests.get(repo_url)
            with open(f"Library-Management-System({version}).zip",'wb') as f:
                f.write(r.content)
            messagebox.showinfo("Info","Please switch to the new version :)")    
            exit()

screen = main()
if exists("info.dat"):
    with open("info.dat",'rb') as file:
        info = pickle.load(file)
        info = eval(base64.b64decode(info).decode("ascii").split("+")[1])
        screen.mysql_username = info['username']
        screen.mysql_password = info['password']
        screen.fine = int(info["fine"])
    screen.login()
else:    
    screen.start()
