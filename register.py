from functools import wraps
from logging import PlaceHolder, raiseExceptions
import re
from unicodedata import name
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask.templating import render_template_string
from flask.wrappers import Request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField, form, meta,validators
from passlib.hash import sha256_crypt
import os
from flask import Flask, render_template, request, redirect, abort, flash, url_for
from werkzeug.utils import secure_filename



app = Flask(__name__)
app.secret_key = "deneme1"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "website"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# Giriş Olma Formu
class LoginForm(Form):
    name = StringField("İsim & Soyisim")
    password = PasswordField("Parola")


# Kullanıcı Kayıt Formu
class RegisterForm(Form):

    code = StringField("Kodu giriniz.") 
    name = StringField("İsim & Soyisim",validators = [validators.length(min = 4,max= 16)])
    email = StringField("Email Adresi",validators = [validators.Email(message="Lütfen Geçerli Bir Email Adresi Giriniz")])
    password = PasswordField("Parola",validators=[

        validators.DataRequired(message="Lütfen bir parola giriniz"),
        validators.EqualTo(fieldname = "confirm",message = "Parolanız Uyuşmuyor...")
    
    ])
    confirm = PasswordField("Parola Doğrula")



#Burada ise tekrar kayıt olma veya giriş yapma durumunu kontrol edip engelliyoruz.

def login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if  not "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Siz zaten giriş yaptınız!","danger")
            return redirect(url_for("index"))
    return decorated_function

def register_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Siz zaten kayıtlısınız!","danger")
            return redirect(url_for("index"))
    return decorated_function


#Ana sayfa
@app.route("/") #Eğer dizin "/" bu ise index.html dosyasını çalıştırıyoruz.
def index():
    return render_template("index.html")


#Kayıt olma işlemi
@app.route("/register",methods = ["GET","POST"])
@register_req
def register():
    
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():       
        code = form.code.data   
        name = form.name.data
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()

        if code == "deneme1": #Buradan kodu ayarlayabilirsiniz.
            sorgu = "Insert into users(Name,Email,Password) Values(%s,%s,%s)"
            cursor.execute(sorgu,(name,email,password))
            mysql.connection.commit()
            cursor.close()

            flash("Başarıyla Kayıt Oldunuz!" , "success")

            return redirect(url_for("login"))
        else:
            flash("Kodunuz hatalı... Lütfen tekrar deneyin.")
            return redirect(url_for("register"))
    else:
        
        return render_template("register.html",form = form)


#Giriş yapma işlemi 
@app.route("/login",methods = ["GET","POST"])
@login_req
def login():
    form = LoginForm(request.form)
    
    if request.method == "POST":
        name = form.name.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()
        
        sorgu = "SELECT * FROM users WHERE Name = %s"
        result = cursor.execute(sorgu,(name,))

        if result > 0 :
            data = cursor.fetchone()
            real_password = data["Password"]

            if (password_entered == real_password):
                flash("Başarıyla giriş yapıldı...","success")

                session["logged_in"] = True
                session["name"] = name

                return redirect(url_for("index"))
            else:
                flash("Parolanızı yanlış girdiniz...","danger")
                return redirect(url_for("login"))

        else:
            flash("Böyle bir kullanıcı bulunmuyor...", "danger")
            return redirect(url_for("login"))

    return render_template("login.html",form = form)



#Çıkış yapma işlemi
@app.route("/logout")
def logout():
    session.clear()
    flash("Çıkış yaptınız.", "success")
    return redirect(url_for("index"))








if __name__ == "__main__":
    app.run(debug=True)

