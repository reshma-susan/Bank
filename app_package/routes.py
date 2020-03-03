from flask import render_template,flash,redirect,url_for
from app_package import app, db,mongo
from flask_login import current_user, login_user, logout_user, login_required
from app_package.forms import LoginForm,RegistrationForm,NewAccountForm,DepositForm,WithdrawalForm,CloseAccountForm,ConfirmForm,BalanceForm
from app_package.models import Employee

id=0
@app.route("/",methods=["GET","POST"])
def index():
    form=LoginForm()
    if form.validate_on_submit():
        employee=Employee.query.filter_by(username=form.username.data).first()
        if employee is None or not employee.check_password(form.password.data):
            flash("Invalid user")
            return redirect(url_for("index"))
        else:
            return redirect(url_for("home"))
    else:
        return render_template("login.html",form=form)
        
@app.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        form=RegistrationForm()
        if form.validate_on_submit():
            if form.password2.data=="bank" :
                employee=Employee(username=form.username.data)
                employee.set_password(form.password.data)
                employee.set_email(form.email.data)
                db.session.add(employee)
                db.session.commit()
                flash("User registered. You may login now")
                return redirect(url_for("index"))
            else:
                flash("Please enter the correct credentials") 
                return render_template("register.html",form=form)
        else:
            return render_template("register.html",form=form)
            
@app.route("/new_account",methods=["GET","POST"])
def new_account():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        form=NewAccountForm()
        if form.validate_on_submit():
            customer_type = dict(form.customer_type.choices).get(form.customer_type.data)
            if int(form.balance.data) >= 50000 and customer_type=="Priority Customer":
                enter_customer(form,customer_type) 
                flash("Customer added")
                return redirect(url_for("home"))
            elif  int(form.balance.data) >= 10000 and customer_type=="Ordinary Customer":
                enter_customer(form,customer_type) 
                flash("Customer added")
                return redirect(url_for("home"))
            else:
                flash("Problem adding customer")
                return redirect(url_for("new_account"))
        else:
            return render_template("new_account.html",form=form)
       
@app.route("/deposit",methods=["GET","POST"])
def deposit() :
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        form=DepositForm()
        if form.validate_on_submit():
            query={"acc_no":form.acc_no.data}
            cus_col=mongo.db.customers
            doc=cus_col.find_one(query)
            if doc is not None:
                bal=doc["balance"]  
                new_bal=int(bal)+int(form.deposit.data)
                new_data={"$set":{"balance":new_bal}}
                cus_col.update_one(query,new_data)
                flash("Amount Deposited")
                return redirect(url_for("home"))
            else:
                flash("No such account")
                return render_template("deposit.html",form=form)
        else:
            return render_template("deposit.html",form=form)


            
@app.route("/withdraw",methods=["GET","POST"])
def withdrawal() :
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        form=WithdrawalForm()
        if form.validate_on_submit():
            withdraw_amount=form.withdraw.data
            query={"acc_no":form.acc_no.data}
            cus_col=mongo.db.customers
            doc=cus_col.find_one(query)
            if doc is not None:
                bal=doc["balance"] 
                cus_type=doc["customer_type"] 
                new_bal=int(bal)-int(withdraw_amount)
                if  new_bal >= 50000 and cus_type=="Priority Customer":
                    enter_withdrawal(new_bal,form,query)
                    flash(str(withdraw_amount)+" is withrawed and new balance is "+str(new_bal))
                    return redirect(url_for("home"))
                elif new_bal >= 10000 and cus_type=="Ordinary Customer":
                    enter_withdrawal(new_bal,form,query) 
                    flash(str(withdraw_amount)+" is withrawed and new balance is "+str(new_bal))
                    return redirect(url_for("home"))
                else:
                    flash("No sufficient balance")
                    return render_template("withdraw.html",form=form)
            else:
                flash("No such account")
                return render_template("withdraw.html",form=form)
        else:
            return render_template("withdraw.html",form=form)
            
@app.route("/home")
def home():
    return render_template("home.html")
    
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
    
@app.route("/display_customers")
def display_customers():
    cus_col=mongo.db.customers
    customers=cus_col.find()
    return render_template("display_customers.html",customers=customers)
    
@app.route("/deleted_account")
def deleted_account():
    del_col=mongo.db.deleted_customers
    customers=del_col.find()
    return render_template("deleted_account.html",customers=customers)
    
def enter_customer(form,customer_type):
    global id
    fields=["_id","acc_no","username","customer_type","balance"]
    id+=1
    values=[id,form.acc_no.data,form.username.data,customer_type,form.balance.data]
    active_customer=dict(zip(fields,values))
    cus_col=mongo.db.customers
    tmp=cus_col.insert_one(active_customer)  
    return tmp.inserted_id
    
def enter_withdrawal(new_bal,form,query):
    new_data={"$set":{"balance":new_bal}}
    cus_col=mongo.db.customers
    cus_col.update_one(query,new_data) 
    
@app.route("/delete",methods=["GET","POST"])
def delete():
    form=CloseAccountForm()
    f2=ConfirmForm()
    if form.validate_on_submit():
        cust_col=mongo.db.customers
        query={"acc_no":form.acc_no.data}
        customers=cust_col.find(query)
        return render_template("confirm.html",f2=f2,customers=customers)  
    else:
        return render_template("delete.html",form=form)        
    
        
@app.route("/confirm",methods=["GET","POST"])
def confirm():
    f2=ConfirmForm()
    cus_col=mongo.db.customers
    query={"acc_no":f2.acc_no.data}
    doc=cus_col.find_one(query)
    bal=doc["balance"]
    name=doc["username"] 
    cus_type=doc["customer_type"] 
    fields=["acc_no","username","customer_type"]
    values=[f2.acc_no.data,name,cus_type]
    deleted_customer=dict(zip(fields,values))
    del_col=mongo.db.deleted_customers
    tmp=del_col.insert_one(deleted_customer)
    cus_col.delete_one(query)
    flash("Customer deleted")  
    return redirect(url_for("home"))

@app.route("/balance",methods=["GET","POST"])
def balance():
    form=BalanceForm()
    if form.validate_on_submit():
        cust_col=mongo.db.customers
        query={"acc_no":form.acc_no.data}
        customers=cust_col.find(query)
        return render_template("display_customers.html",customers=customers)  
    else:
        return render_template("balance.html",form=form)   

