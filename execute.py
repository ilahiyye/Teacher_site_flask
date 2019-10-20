import os 
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, abort, send_file, send_from_directory
from flask_mysqldb import MySQL                                             
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import MySQLdb.cursors
from functools import wraps                                                                                                                        #istifadeci giris decoratorunu yazmaq ucun import edirik
from werkzeug.utils import secure_filename




###################### Istifadeci giris decorator #############################################################

def login_required(f):                  
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" in session:                                                                                                                   #yeni session lugetinde istifadeci varmi deye yoxlayiriq
            return f(*args, **kwargs)
        else:                                                                                                                                       #istifadecinin giris edib-etmediyini yoxlayiriq ki diger sehifelere girmek olsun)
            flash("Sayta daxil olun və ya qeydiyyatdan keçin", category="danger")
            return redirect("/")   
        
    return decorated_function

###################### Admin giris decoratoru   ######################

def special_requirement(f):
    @wraps(f)
    def admin(*args, **kwargs):
        if "ilahiye" == session["username"]:                                                                                                        #giris edenin adminolub-olmadigini yoxlayir
            return f(*args, **kwargs)
        else:
            flash("sizə bu emeliyyati yerine yetirmeye icaze verilmir", category="danger") 
            return redirect(url_for("index"))
    return admin

##################### Faylin uzantisini yoxlayan funksia ##############

def allowed_file(file_name):                                                                                                                        #guvenlik ucun yazilmis funksiyadir. yuklenenfunksiyanin yuxaridaki filltipinden olub-olmadigini yoxlayir
    return '.' in file_name and file_name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

######################  FORUMLAR   ###################################

class SignForm(Form):                                                                                                                               #wtform kitabxanasindan istifade edeceyik    
    name    = StringField("İstifadəçi adınız", validators = [validators.Email(message ="Doğru e-poçt ünvanı girin!")])
    password = PasswordField("Şifrə", validators = [validators.DataRequired(message ="Şifrənizi daxil edin!")])   


class RegisterForm(Form):
    FirstName= StringField  ("Ad",     validators = [validators.Length(min=3, max = 15, message="Ən azi 3 hərf daxil etməlisiz...")])               #validators input kimi daxiletdiyimiz deyisene mehdudiyyet veririk. min=3 max=15 uzunluqda
    LastName = StringField  ("Soyad",  validators = [validators.Length(min=3, max=15, message="Ən azi 3 hərf daxil etməlisiz...")]) 
    name     = StringField  ("İstifadəçi adı", validators = [validators.Length(min=3, max=15, message="Ən azi 3 hərf daxil etməlisiz...")])         #Input sahesidi. name text olmasi ucun stringField clasindan istifade olunur.
    sector   = StringField  ("Qrup",   validators = [validators.DataRequired(message ="Bu hissə yazılmalıdı!")])
    email    = StringField  ("E-poçt", validators = [validators.Email(message ="Doğru e-poçt ünvanı girin!")])
    password = PasswordField("Şifrə",  validators = [validators.DataRequired(message ="Şifrənizi daxil edin!"),                                     #validators.Datarequire mutleq doldurulmali olan hissedi
               validators.EqualTo(fieldname = "confirm", message="Şifrələr eyni deyil...")                                                          #validators.EqualTo confiq hissedeki yazilanlarin uygunlugu yoxlayacaq
               ])
    confirm  = PasswordField("Şifrəni təsdiq et")
      
class ArticleForm(Form):
    title   = StringField  ("Məqalənin başlığı", validators = [validators.Length(min = 4)])                                                          #Meqalenin adini yaza bilecek bir sahe yaradir.Min 4 herif daxil edilmelidir
    content = TextAreaField("Məqalənin mətni", validators = [validators.Length(min = 15)] )                                                          #Meqale yazilacaq yer boyuk oldugu ucun TextAreaField den istifade edilir. Meqale min 15 herifden ibaret olmalidir

#######################################################################################################################################################################################################################################

#Sayta fayl yuklemek ucun
UPLOAD_FOLDER = 'static/uploads'                                                    #Sayta yuklenen fayillar bu unvana gedecek. burada "/" bunun olmasina fikir ver
#PDF_FOLDER = "static/pdf"
#IMG_FOLDER = "/static/gallery"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'docx', 'jpg', 'jpeg', 'gif'])       #Fayillarin uzantilaridir. Hansi ki ancaq bu fayillari yuklemek olar


app = Flask(__name__)

app.secret_key="4"                                                                              

########## MYSQL confiqurasiyasi #########################################          #Configurasiyaya https://flask-mysqldb.readthedocs.io/en/latest/ burdan baxa bilersen

app.config["MYSQL_HOST"]        = "localhost"                                       #Local hostda islediyinden onun adini yaziriq
app.config["MYSQL_USER"]        = "root"                                            #XAMPP da user: root kimi yazilib
app.config["MYSQL_PASSWORD"]    = ""                                                #XAMPP da mysql qosulmaq ucun password teyin etmemisik ""
app.config["MYSQL_DB"]          = "students"                                        #Burada DB in adini yaziriq
app.config["MYSQL_CURSORCLASS"] = "DictCursor"                                      #DictCursor, yeni db melumatlar luget(dictonary) seklinde otrulur
app.config['UPLOAD_FOLDER']     = UPLOAD_FOLDER                                     #Sayta yuklenen fayillar UPLOAD_FOLDER  papqasina dusecek
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024                                #max 16 Mb file yuklemek mehdudiyyeti veririk

mysql = MySQL(app)                                                                  #Mysql ile Flask arasinda elaqe qurulmus olduq


@app.route("/", methods =["GET","POST"])            
def input():
    form = SignForm(request.form)

    if request.method == "POST":
        name = form.name.data
        password_in = form.password.data
        
 #dbdeki melumatla ust-uste dusduyunu yoxlamaliyiq Bunu tek-tek yoxlayiriq
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)                #evvel ada gore yoxlayiriq varsa, parollar muqayise edilecek. Sorgu cedveldeki ada uygun butun melumatlari secir
        result = cursor.execute("SELECT * FROM  users WHERE name = (%s)",(name, ))  #eger db de bele ad varsa result 0 dan boyuk? yoxdursa 0 olacaq

        if result>0:                                                                #yeni girilen adda adam vars,
            lug = cursor.fetchone()                                                 #data lugetine hemin istifadeci haqqqinda butun girilen melumatlar yazilir
            password_real = lug["password"]                                         #data["password"] yazaraq user cedvelindeki heqiqi parolu aliriq. Ancaq sifreli bir veziyyetde
            
            if sha256_crypt.verify(password_in,password_real):                      #sha256_crypt.verify() funksiyasi passwordlarin sifrelerini acaraq dogruluqlarini yoxlayir
                flash("Təkrar xoş gəldin!", category="success")                     #eger parol duzdurse bu mesaj ana sehifede gorunecek
                session["input"] = True                                             #session da luget kimidir. Ona "input" acar sozunu verirem
                session["username"] = name                                          #session basladilib/ Harda? giris edildikden sonra
                return redirect(url_for("index"))

            else:
                flash("Yalnış parol!",category="danger")                            #Eger parol sehvdirse bu mesaj ele hemin sehifenin ozunde gorunsun
                return render_template("login.html", form=form)
        else:
            flash("Təəssüf ki, belə istifadəçi qeydiyyatdan keçməyib...",category="danger")  #qirmizi rengde gorsenecek
            return render_template("login.html", form=form)                         #qeydiyyatdan kecmediyi ucun sehife yene ozune qayitsin
        cursor.close()
    
    else:             
       return render_template("login.html",form = form)                             #GET request edildiyi zamani sehifede form gorunmesini temin edir

########### Registrasiya Sehifesi#########################################
@app.route("/register", methods = ["GET","POST"])                                   #method.la sehifenin hem Get request, hem de SET request oldugunu gosterir 
def register():
    form = RegisterForm(request.form)                                               #eger sehifemize post request atilarsa, RegistForum.na girilen melumatlar RegistrFormda olacaq, bizde onu form vasitesi ile db gondereceyik
    if request.method == "POST" and form.validate():                                #hem de (form.validate()) ile formmuzun duzgun dolduruldugunu yoxlayir ve ondan sonra ana sehifeye giris edir.

        #Evvel foruma girilen melumatlari aliriq
        FirstName= form.FirstName.data
        LastName = form.LastName.data                                               #forma daxil edilen melumatlari .data deyerek aliriq
        name     = form.name.data      
        sector   = form.sector.data
        email    = form.email.data
        password = sha256_crypt.encrypt(form.password.data)                         #sifreni kodlasdiraraq formdan aliriq
        
        #bu datalari vb cedvele daxil etmeliyik
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO users VALUES(NULL,%s,%s,%s,%s,%s,%s)",(FirstName, LastName, name, sector, email, password))
        mysql.connection.commit()                                                   #bunu yazmasan db ine data yazilmayacaq
        session["username"] = name
        cursor.close()
        flash("Qeydiyyatınız uğurlu oldu!", category="success")                     #index sehifesinde gorunecek mesaj. Cemi bir defe o da yeni qeydiyyatdan kecdikde
        return redirect(url_for("index"))                                           #sehifede post request edildikde(yeni, buttonu basdiqda) redirect(url_for) komeyi ile home sehifesine daxil olacagiq

    else:
        return render_template("register.html", form = form)                        #Brada yaratdigimiz form.u register.html sehifesine gondereceyik


#################### Ana sehife ##########################################
@app.route("/index")
@login_required
def index():                                                                        #Burasi bizim ana sehifemizdir ve burada meqaleler gosterilecek
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sorgu  = "SELECT * FROM articles"                                               #VB daki articles cedvelindeki butun verilenleri secirik
    result = cursor.execute(sorgu)
    
    if result>0:                                                                    #Yeni vb da meqale varsa.fetchone bir setri secir, fetchall ise butun deyisenleri secir
        articles = cursor.fetchall()                                                #fetchall butun meqaleleri liste seklinde cekir ve articles menimsedir. 
        return render_template("index.html", articles = articles)                   #articles = articles yazaraq onu index.html sehifesinde gosteririk
    else:
        return render_template("index.html")
    
    cursor.close()
    return render_template("index.html")

############## Ana sehifedeki faylin id-ne gore acir ##################### 
@app.route("/index/<string:id>")                                                    #bunu ona gore yaziriq ki verilenler bazasindaki ixtiyari bir id ye gore verileni tapaq
@login_required                                                                     #Bu sehifede ancaq Get request olur
def article(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sorgu  = "SELECT * FROM articles WHERE id = %s"                                  #VB daki articles cedvelindeki butun verilenleri secirik
    result = cursor.execute(sorgu, (id,))                                            #id ye gore db de axtaris edirik
    if result>0:
        article = cursor.fetchone()                                                  #id unvan unical oldugundan ona uygun bir dene meqale gelecek
        return render_template("content.html", article = article)
    else:
        return render_template("content.html")                                      # "" UNUTMA!

################# Control Panel ###########################################
@app.route("/index/control_panel", methods=["GET","POST"])
@login_required
def control():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sorgu  = "SELECT * FROM articles"
    result = cursor.execute(sorgu)

    if result>0:                                                                   #Yeni vb da meqale varsa.fetchone bir setri secir, fetchall ise butun deyisenleri secir
        articles = cursor.fetchall()                                               #fetchall butun meqaleleri liste seklinde cekir ve articles menimsedir. 
        return render_template("control.html", articles = articles)                #articles = articles yazaraq onu index.html sehifesinde gosteririk

    else:
        return render_template("control.html")

    cursor.close()
    return render_template("control.html")

######### Meqalelerin idare edilmesi #######################################
@app.route("/index/control/addarticles", methods=["GET","POST"])
@login_required
def addarticle():
    form = ArticleForm(request.form)

    if request.method == "POST" and form.validate():                                #Yazilan meqaleleri db daxil edek
        title   = form.title.data                                                   #Form.a yazilan datalari aliriq
        content = form.content.data
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sorgu  = "INSERT INTO articles(title, author, content) VALUES (%s,%s,%s)"
        cursor.execute(sorgu,(title, session["username"], content))
        mysql.connection.commit()   
        cursor.close()

        flash("Məqaləniz Uğurla Yükləndi", "success")                               #success, yeni yasil rengli ugurlu mesaj                
                                                                                    #url_for hissesine funksiyanin adini yaziriq
        return redirect(url_for("control"))                                         #Meqaleni yazdiqdan sonra ele hemin sehifeye qayidiriq

    return render_template("addarticles.html", form=form)

############# Meqalenin silinmesi ############################################
@app.route("/delete/<string:id>")                                                   #bunu ona gore yaziriq ki verilenler bazasindaki ixtiyari bir id ye gore verileni tapaq
@login_required
def delete(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sorgu1 = "SELECT * FROM articles WHERE id = %s and author = %s"                 #giris eden sexs basqasinin meqalesini sile bilmesin deye birinci sorgunu yaziriq
    result = cursor.execute(sorgu1,(id, session["username"],))                      #author.a ve id gore meqaleleri tapacaq

    if result>0:
        sorgu2 = "DELETE FROM articles WHERE id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        return redirect(url_for("control"))

    else:
        flash("Sizə bu məqaləni silməyə icazə verilmir", category="warning")
        return redirect(url_for("index")) 

    cursor.close()

############ Meqalede duzelis etmek ############################################
@app.route("/edit/<string:id>", methods = ["GET","POST"])                          #bunu ona gore yaziriq ki verilenler bazasindaki ixtiyari bir id ye gore verileni tapaq
@login_required
def update(id):

    if request.method == "GET":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        sorgu1 = "SELECT * FROM articles WHERE id = %s and author = %s"            #giris eden sexs basqasinin meqalesini sile bilmesin deye birinci sorgunu yaziriq
        result = cursor.execute(sorgu1,(id, session["username"],))   

        if result > 0:
            article = cursor.fetchone()                                            #Artiq butun cedvel dict seklinde articldadir
            form = ArticleForm()
            form.title.data   = article["title"]                                   #Formun icine title ve content yazilari yazdirirq
            form.content.data = article["content"]
            return render_template("update.html", form = form)
        e
        lse: #db-de melumat tapilmadiqda
             flash("Sizə bu məqalənin üzərində dəyişiklik etməyə sizə icazə verilmir", category="warning")
             return redirect(url_for("index")) 

    else: #POST request
        form = ArticleForm(request.form)                                            #request.form ederek formun icindeki melumatlari gotururuk
        newtitle   = form.title.data
        newcontent = form.content.data
        sorgu2 = "UPDATE articles SET title = %s, content = %s WHERE id=%s"         #Melumatla; db-de yenileyirik.
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)                #cursormuzu yeniden yaradiriq
        cursor.execute(sorgu2, (newtitle,newcontent,id,))
        mysql.connection.commit()
        flash("Məqaləyə isdədiyiniz düzəlişlər uğurla edildi", category="success")
        return redirect(url_for("control"))


#################### SEKILLER ###################################################
@app.route("/index/gallery/<image_name>")
@login_required
def gallery(image_name):
    return render_template("gallery.html")


#################### Ferdi isler ################################################
@app.route("/index/pers")                                                               #dosyayukleme
@login_required
def pers():
    return render_template("pers.html")

################# Fayil yukleme sehifesi-netice ################################
@app.route("/index/pers/<string:dosya>")
@login_required
def netice(dosya):
    return render_template("pers.html", dosya = dosya)

############### Fayl yukleme emeliyyati ########################################
@app.route("/index/upload_file", methods = ["POST"])                                    #burda ancaq post request olmalidir
@login_required
def upload_file():
    
    if request.method == 'POST':
    # formdan file yuklenib-yuklenmediyini yoxlayiriq
        if 'dosya' not in request.files:
            flash('File seçilmədi', category="danger")
            return redirect('pers')
    
    # əgər istifadeci fayl secmeyibse ve adsiz file secibse     
        dosya = request.files['dosya']  
        if dosya.filename == '':
            flash('Fayl seçilməyib', category="warning")
            return redirect('pers')
        
    # yuklenen fayillar guvenlik yoxlamalarindan kecirilir
        if dosya and allowed_file(dosya.filename):                                      #faylin uzantisini yoxlayir
            file_name = secure_filename(dosya.filename)                                 #guvenlik meqsedi ile isdifadecinin gonderdiyi filein adi qismen deyisdirilir 
            basedir = os.path.abspath(os.path.dirname(__file__))
            dosya.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], file_name))
            flash('Fayl uğurla yükləndi', category = "success")
            return redirect('pers/' + file_name)                                        #upload_file/ hissesine diqqet. redirect funksiyanin adina gore hereket edir. bura hecmin de yoxlayan serti

        else:
            flash("Zəhmət olmasa txt, pdf, png, jpg, jpeg, gif tipli bir fayl yukleyin", category="danger")
            return redirect('pers')
    else:
        abort(401)                                                                      #sehv oldugun gosterir                                      


############### Muhazireler sehifesi #########################################
@app.route('/index/books/')
@login_required
def books():
    return render_template ("books.html")

@app.route('/return-files/', methods=["POST"])
@login_required
def return_files():
    file_name = "C:/Users/Ilahiye/Desktop/Proyektlerim/Flask_telebe/static/pdf/Qraflar_nezeriyyesi.pdf"
    return send_file(open(file_name), mimetype='Qraflar_nezeriyyesi/pdf', as_attachment=True, attachment_filename='Qraflar_nezeriyyesi.pdf')
app.route('/return-files1/', methods=["POST"])
def return_files_1():
    file_name_1 = "C:/Users/Ilahiye/Desktop/Proyektlerim/Flask_telebe/static/pdf/Qraf_kitab_turkce.pdf"
    return send_file(open(file_name_1), mimetype='Qraflar_nezeriyyesi/pdf', as_attachment=True, attachment_filename='Qraf_kitab_turkce.pdf')

@app.route('/index/pdf-file/')
@login_required
def pdf_1():
    pdf_path = 'C:/Users/Ilahiye/Desktop/Proyektlerim/Flask_telebe/static/pdf/Avto_lay_sis.pdf'
    return send_file(open(pdf_path), mimetype='Avto_lay_sis/pdf', as_attachment=True, attachment_filename='Avto_lay_sis.pdf')


@app.route('/index/pdf/')
@login_required
def pdf_2():
    resp = "C:/Users/Ilahiye/Desktop/Proyektlerim/Flask_telebe/static/pdf/KALS.pdf"
    return send_file(resp, attachment_filename='KALS.pdf')                                  #mimetype='KALS/pdf', as_attachment=True

####################################################################################################################################################


@app.route("/index/sillabus")
@login_required
def sillabus():
    return render_template("sillabus.html")
@app.route("/index/video")
@login_required
def video():
    return render_template("video.html")

################ Logout ######################################################
@app.route("/index/log_out")
@login_required
def log_out():
    session.clear()
    return redirect("/")                                                                    #Bununla biz cixis ederken birinci(login) sehifeye qayidacagiq. Redirect.e tekce root.u verdim

if __name__ == "__main__":
    app.run(debug=True)

