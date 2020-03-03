from app_package import db,login_manager
from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256 as pbsha

@login_manager.user_loader
def load_user(id):
    return Employee.query.get(id)
    
class Employee(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),unique=True)
    password=db.Column(db.String(128))
    email=db.Column(db.String(128))


    def set_password(self,password):
        self.password=pbsha.hash(password)
    
    def check_password(self,password1):
        return pbsha.verify(password1,self.password)
       
    def set_email(self,email):
        self.email=email; 
    
