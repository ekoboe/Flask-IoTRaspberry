import time
import board
import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint
import random
from gpiozero import LED          
from gpiozero import Button
from time import sleep
from flask_apscheduler import APScheduler
from sqlalchemy.sql import func
from script.weather import get_weather
from script.greeting import get_greeting

from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

import serial
uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)
uart2 = serial.Serial("/dev/ttyUSB1", baudrate=57600, timeout=1)


finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
finger2 = adafruit_fingerprint.Adafruit_Fingerprint(uart2)

##################################################
from flask import Flask, request, flash, session, url_for, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import RPi.GPIO as GPIO
app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartroom.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)

    
class Door(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float)
    first = db.Column(db.String)
    later = db.Column(db.String)
    daya = db.Column(db.Float)
    dayalampu = db.Column(db.Float)
    dayaac = db.Column(db.Float)
    dayapower = db.Column(db.Float)
    kwh = db.Column(db.Float)
    rupiah = db.Column(db.Float)
    lampusaja = db.Column(db.Float)
    totalbaru = db.Column(db.Float)
    dayabaru = db.Column(db.Float)
    kwhbaru = db.Column(db.Float)
    rupiahbaru = db.Column(db.Float)
    created = db.Column(db.DateTime, nullable=True,default=datetime.today)
    
class Lampu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    totallampu = db.Column(db.Float)
    start = db.Column(db.String)
    end = db.Column(db.String)
    created = db.Column(db.DateTime, nullable=True,default=datetime.today)
    
db.create_all()

class LoginForm(FlaskForm):
    email = StringField(validators=[
        InputRequired(), Length(min=1, max=20)])

    password = PasswordField(validators=[
        InputRequired(), Length(min=1, max=20)])

    submit = SubmitField('Login')

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        session['username'] = user.name
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))

    return render_template('login.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def loginlagi():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        session['username'] = user.name
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
        
    return render_template('login.html', form=form)

@app.route('/veriflogin1')
def get_fingerprint():
    """Get a finger print` image, template it, and see if it matches!"""
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    if finger.finger_fast_search() != adafruit_fingerprint.OK:
        return False
    return True

@app.route('/veriflogin2')
def verifikasi():
    if get_fingerprint():
        return redirect(url_for('user'))
    else:
        flash('Failed, try again')
        return redirect(url_for('login'))
    
@app.route('/veriflogin3')
def get_fingerprint2():
    """Get a finger print` image, template it, and see if it matches!"""
    while finger2.get_image() != adafruit_fingerprint.OK:
        pass
    if finger2.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    if finger2.finger_fast_search() != adafruit_fingerprint.OK:
        return False
    return True

@app.route('/veriflogin4')
def verifikasi2():
    if get_fingerprint2():
        return redirect(url_for('user'))
    else:
        flash('Failed, try again')
        return redirect(url_for('login'))


@app.route('/formRegister')
def formRegister():
    return render_template('register.html')


@app.route('/registerProses', methods=['POST'])
def proses_register():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user:
        flash('Email Sudah ada')
        return redirect(url_for('formRegister'))
    
    hashed_password = bcrypt.generate_password_hash(password)
    new_user = User(email=email, name=name, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session.pop('username', None)
    return redirect(url_for('login'))

###############################################################
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(2, GPIO.OUT)
GPIO.output(2, GPIO.LOW)
GPIO.setup(3, GPIO.OUT)
GPIO.output(3, GPIO.LOW)
GPIO.setup(4, GPIO.OUT)
GPIO.output(4, GPIO.LOW)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.LOW)
led = LED(4)
button = Button(17)
##################################################################

def fungsi():
        print("zzzzzzzzzzzzz")
        while True:
            if button.wait_for_press():
                led.off()
                sleep(1)
                start = datetime.now()
                session['start'] = start
                
            if button.wait_for_press():
                led.on()
                print("hhhhhhhhhh")
                sleep(1)
                start_time = session['start']
                tawal = (end.hour*3600)+(end.minute*60)+(end.second)
                takhir = (start.hour*3600)+(start.minute*60)+(start.second)
                totallampu = ((tawal - takhir)/3600)
                user = Lampu(totallampu=totallampu, start=start_time, end=end)
                db.session.add(user)
                db.session.commit()
                
def refunc():
    return fungsi()
    
@app.route('/home')
@login_required
def home():
    greet = get_greeting()
    return render_template('index.html', greet=greet, button = GPIO.input(17), lampu = GPIO.input(4), door = GPIO.input(2), brankas = GPIO.input(3))

@app.route("/<deviceName>/<action>")
def action(deviceName, action):
    if deviceName=='led':
        actuator=led
    
    if action=="on":
        GPIO.output(actuator, GPIO.HIGH)
    if action=="off":
        GPIO.output(actuator, GPIO.LOW)
    
    ledSts=GPIO.input(led)
    
    templateData={
        'led':ledSts,
        }
    return render_template('index.html', **templateData)

@app.route('/user')
def user():
    return render_template('user.html', user = User.query.all())

@app.route('/find')
def find():
    if get_fingerprint():
        flash("Detected, template number %i" % finger.finger_id)
        return render_template('find.html', user = User.query.all())
    else:
        flash('Finger not found')
        return render_template('find.html', user = User.query.all())
    
@app.route('/enrollf')
def enrollf():
    if enroll_finger():
        return render_template('enroll.html', user = User.query.all())
    else:
        flash('Failed, try again')
        return render_template('enroll.html', user = User.query.all())
@app.route('/enroll')
def enroll():
    return redirect(url_for('tambah'))
    
@app.route('/fungsienr')
def enroll_finger():
    location = random.randint(5, 127)
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            pass
        else:
            pass

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                break
            elif i == adafruit_fingerprint.NOFINGER:
                pass
            elif i == adafruit_fingerprint.IMAGEFAIL:
                flash("Imaging error")
                return False
            else:
                flash("Other error")
                return False

        
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            pass
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                flash("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                flash("Could not entify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                flash("Image invalid")
            else:
                flash("Other error")
            return False

        if fingerimg == 1:
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        pass
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            flash("Prints did not match")
        else:
            flash("Other error")
        return False

    
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        flash("Stored in template %i" % location)
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            flash("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            flash("Flash storage error")
        else:
            flash("Other error")
        return False

    return True

@app.route('/del')
def yyy():
    return render_template('delete.html', user = User.query.all())
    
@app.route('/delete', methods=['POST'])
def delete():
    if finger.delete_model(int(request.form.get('template'))) == adafruit_fingerprint.OK:
        flash("Deleted!")
    else:
        flash("Failed to delete")
    
    return render_template('delete.html', user = User.query.all())

@app.route('/usage')
def usage():
    data = Door.query.all()
    data1 = []
    data2 = []
    data3 = []
    data4 = []
    data5 = []
    data6 = []
    data7 = []
    create = []
    #tes = (sum([Door.totallampu for totallampu in data1]))
    for amounts in data:
        data1.append(amounts.total)
        data2.append(amounts.daya)
        data3.append(amounts.kwh)
        data4.append(amounts.rupiah)
        data5.append(amounts.dayalampu)
        data6.append(amounts.dayaac)
        data7.append(amounts.dayapower)
        create.append(amounts.created.strftime('%H:%M'))
    return render_template('usage.html', smartroom=data, rupiah=data4, dayalampu=data5, dayaac=data6, dayapower=data7, kwh=data3, daya=data2, total=data1, create=create, lampu = GPIO.input(4))

@app.route('/door')
def door():
    return render_template('door.html', button = GPIO.input(17), door = GPIO.input(2), lampu= GPIO.input(4))

@app.route('/nyala')
def nyala():
    if get_fingerprint():
        first_time = datetime.now()
        session['first'] = first_time
        GPIO.output(2, GPIO.HIGH)
        GPIO.output(4, GPIO.HIGH)
        flash("Pintu dibuka oleh nomor %i" % finger.finger_id)
        #schedule.every().seconds.do(func)
        #scheduler.add_job(id='refunc', func=refunc, trigger="interval", seconds=2)
        while True:
            if button.wait_for_press():
                led.off()
                sleep(1)
                start = datetime.now()
                session['start'] = start
            if button.wait_for_press():
                led.on()
                sleep(1)
                end = datetime.now()
                start_time = session['start']
                tawal = (end.hour*3600)+(end.minute*60)+(end.second)
                takhir = (start.hour*3600)+(start.minute*60)+(start.second)
                totallampu = round((tawal - takhir)/3600, 6)
                user = Lampu(totallampu=totallampu, start=start_time, end=end)
                db.session.add(user)
                db.session.commit()
                break
            #if GPIO.input(2) == 0:
            #   print("aaaaaaaaaaaaa")
            #elif GPIO.input(2) == 1:
            #   print("hhhhhhhhhh")
                #end = datetime.now()
        return render_template('door.html', door = GPIO.input(2), lampu = GPIO.input(4))
    else:
        flash("Sidik jari tidak sesuai, tidak dapat membuka pintu")
        return render_template('door.html', door = GPIO.input(2),lampu = GPIO.input(4))
        

@app.route('/matibutton')
def matibutton():
        first_time = session['first']
        later_time = datetime.now()
        later_time = later_time.replace(microsecond=0)
        tawal = (later_time.hour*3600)+(later_time.minute*60)+(later_time.second)
        takhir = (first_time.hour*3600)+(first_time.minute*60)+(first_time.second)
        time_diff = ((tawal - takhir)/3600)
        first = str(first_time)
        later = str(later_time)
        total = round(time_diff, 6)
        lampu = 20
        ac = 600
        power = 70
        dayaac = round((ac)*total, 6)
        dayalampu = round((lampu)*total, 6)
        dayapower = round((power)*total, 6)
        daya = round((lampu + ac + power)*total, 6)
        kwh = round(daya / 1000, 6)
        rupiah = round(kwh * 1352, 6)
        
        lampusaja = db.session.query(func.sum(Lampu.totallampu).label('totalsaja')).first()
        lamputok = str(lampusaja)
        a=lamputok.replace('(','')
        b=a.replace(')','')
        c=b.replace(',','')
        onlylampu = float(c)
        
        totalbaru = total-onlylampu
        dayabaru = (daya - dayalampu)
        kwhbaru = round(dayabaru / 1000, 6)
        rupiahbaru = round(kwhbaru * 1352, 6)
        
        new_user = Door(rupiahbaru=rupiahbaru, kwhbaru=kwhbaru, dayabaru=dayabaru, totalbaru=totalbaru, lampusaja=onlylampu, dayalampu=dayalampu, dayaac=dayaac, dayapower=dayapower,total=total, first=first, later=later, daya=daya, kwh=kwh, rupiah=rupiah)
        #user = Lampu(totallampu=totallampu, dayabaru=dayabaru, kwhbaru=kwhbaru, rupiahbaru=rupiahbaru)
        db.session.add(new_user)
        #Lampu.query.delete()
        db.session.commit()
        GPIO.output(2, GPIO.LOW)
        GPIO.output(4, GPIO.LOW)
        return render_template('door.html', door = GPIO.input(2),lampu = GPIO.input(4))

@app.route('/mati')
def mati():
    if get_fingerprint():
        
        GPIO.output(2, GPIO.LOW)
        flash("Pintu ditutup oleh nomor %i" % finger.finger_id)

        return render_template('door.html', door = GPIO.input(2), lampu = GPIO.input(4))
    else:
        flash("Sidik jari tidak sesuai, tidak dapat membuka pintu")
        return render_template('door.html', door = GPIO.input(2), lampu = GPIO.input(4))


@app.route('/pushbutton')
def pushbutton():
    while True:
        button.wait_for_press()
        led.on()
        print ("nyala")
        sleep(1)
        button.wait_for_press()
        led.off()
        print ("off")
        sleep(1)

@app.route('/matibutton2')
def matibutton2():
    GPIO.output(3, GPIO.LOW)
    return render_template('brankas.html', brankas = GPIO.input(3))

@app.route('/brankas')
def brankas():
    return render_template('brankas.html', brankas = GPIO.input(3))

@app.route('/nyalabrankas')
def nyalabrankas():
    if get_fingerprint2():
        GPIO.output(3, GPIO.HIGH)
        flash("Brankas dibuka oleh nomor %i" % finger2.finger_id)
        return render_template('brankas.html', brankas = GPIO.input(3))
    else:
        flash("Sidik jari tidak sesuai, tidak dapat membuka brankas")
        return render_template('brankas.html', brankas = GPIO.input(3))

@app.route('/matibrankas')
def matibrankas():
    if get_fingerprint2():
        GPIO.output(3, GPIO.LOW)
        flash("Brankas ditutup oleh nomor %i" % finger2.finger_id)
        return render_template('brankas.html', brankas = GPIO.input(3))
    else:
        flash("Sidik jari tidak sesuai, tidak dapat membuka Brankas")
        return render_template('brankas.html', brankas = GPIO.input(3))

@app.route('/first')
def first():

    first_time =datetime.now()
    session['pertama'] = first_time

    return render_template('tes1.html')

@app.route('/later')
def later():
    later_time = datetime.now()
    first_time = session['pertama']
    tawal = (later_time.hour*3600)+(later_time.minute*60)+(later_time.second)
    takhir = (first_time.hour*3600)+(first_time.minute*60)+(first_time.second)
    time_diff = ((tawal - takhir)/3600)
    first = str(first_time)
    later = str(later_time)
    total = time_diff
    lampu = 20
    ac = 600
    power = 70
    daya = ((lampu + ac + power)*total)
    kwh = (daya/1000)
    rupiah = kwh * 1352

    new_user = Door(total=total, first=first, later=later, daya=daya, rupiah=rupiah)
    db.session.add(new_user)
    db.session.commit()
    # return str(time_diff)
    return render_template('tes1.html')

@app.route("/update_weather", methods=['POST'])
def update_weather():
    '''
    Returns updated weather, called every 10 minutes
    '''
    currentWeather = get_weather()
    return jsonify({'result': 'success', 'currentWeather': currentWeather})


if __name__ == "__main__":
    app.run(debug=False, host='192.168.101.80', port=5000)