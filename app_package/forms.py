from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,SelectField,HiddenField
from wtforms.validators import DataRequired,EqualTo,ValidationError
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import Required
from app_package.models import Employee

class LoginForm(FlaskForm):
    username=StringField("Username: ",validators=[DataRequired()])
    password=PasswordField("Password: ",validators=[DataRequired()])
    submit=SubmitField("Sign In")
    
class RegistrationForm(FlaskForm):
    username=StringField("Username: ",validators=[DataRequired()])
    password=PasswordField("Password: ",validators=[DataRequired()])
    password2=PasswordField("Enter Bank Password: ",validators=[DataRequired()])
    email=StringField("Email: ",validators=[DataRequired()])
    submit=SubmitField("Register")
    
    def validate_username(self,username):
        user=Employee.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username exists,choose another one")
    
class NewAccountForm(FlaskForm):
    username=StringField("Name: ",validators=[DataRequired()])
    acc_no=StringField("Account Number: ",validators=[DataRequired()])
    customer_type= SelectField("Customer Type: ",[DataRequired()],choices=[('1', 'Ordinary Customer'), ('2', 'Priority Customer')])
    balance=StringField("Balance: ",validators=[DataRequired()])
    submit=SubmitField("Create Account")
    
class DepositForm(FlaskForm):
    acc_no=StringField("Account Number: ",validators=[DataRequired()])
    deposit=StringField("Deposit Amount: ",validators=[DataRequired()])
    submit=SubmitField("Deposit")
    
class WithdrawalForm(FlaskForm):
    acc_no=StringField("Account Number: ",validators=[DataRequired()])
    withdraw=StringField("Withdrawal Amount: ",validators=[DataRequired()])
    submit=SubmitField("Withdraw")
    
class CloseAccountForm(FlaskForm):
    acc_no=StringField("Account Number: ",validators=[DataRequired()])
    submit=SubmitField("Remove account")
      
class ConfirmForm(FlaskForm):
    acc_no=StringField("Account Number: ",validators=[DataRequired()])
    submit=SubmitField("Confirm")

class BalanceForm(FlaskForm):
    acc_no=StringField("Account Number: ",validators=[DataRequired()])
    submit=SubmitField("Check Balance")

    
