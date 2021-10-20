
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import orm

app = Flask(__name__)
db = SQLAlchemy()
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://umer:hellohello@umer.mysql.pythonanywhere-services.com/umer$data"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost:3306/data"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config['SECRET_KEY'] = "random string"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

class Todo(db.Model):
    __tablename__ = "todo"
    sno = db.Column(db.Integer, primary_key=True)
    user_id =db.Column(db.Integer)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.Text(500), nullable=False)
    date_created = db.Column(db.Date, default=datetime.now())

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date_created = db.Column(db.DATETIME, default=datetime.utcnow(), nullable=False)


    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"

@app.route('/', methods=['GET', 'POST'])
def home():
    
    if not session.get('username'):

         flash('login first !','info')
         return render_template ('login.html')
    else:
        
          allTodo = Todo.query.filter(Todo.user_id == session['id']).all()    
        
         
          if request.method=='POST':
            
            title = request.form['title']
            desc = request.form['desc']
            uid = session['id']
            todo = Todo(title=title, desc=desc,user_id=uid)
            db.session.add(todo)
            db.session.commit()
        
            allTodo = Todo.query.filter(Todo.user_id == session['id']).all()
            return render_template('index.html', allTodo=allTodo) 

    return render_template('index.html',allTodo=allTodo)

@app.route("/login", methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == "POST":

        email = request.form.get("email1")
        password = request.form.get("password1")
        
       

        user = User.query.filter_by(email=email, password=password).first()
        
    
        if user :
            session['username'] = email
            session['name'] = user.name
            session['id'] = user.id
            session['phone'] = user.phone
            
            if not session['username']=='khansahabumer@gmail.com':
                flash('Wellcome in ','success')
                return redirect(url_for("home"))
                
            else:
                session['admin']= user.email
                flash('Wellcome!','success')
                return redirect(url_for("table"))
            

        else:
            flash('Username and password doesnot match','warning')

    return render_template("login.html")

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method=='POST':
        title = request.form['title']
        desc = request.form['desc']
        
        todo = Todo.query.filter_by(sno=sno).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/")
        
    todo = Todo.query.filter_by(sno=sno).first()
    return render_template('update.html', todo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")

@app.route("/reg", methods=['GET', 'POST'])
def reg():

    if request.method == "POST":
        name = request.form.get("name").lower()
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")

        user = User.query.filter_by(email=email).first()
        if not user:
            # Creat new record

            usere = User(name=name, email=email,
                         password=password, phone=phone)

            db.session.add(usere)
            db.session.commit()
            flash('Successfully register!','success')
            return render_template("login.html")

        else:
            flash('Username or Email already exists','danger')
            return render_template("reg.html")

    return render_template("reg.html")

@app.route("/table", methods=['GET','POST'])
def table():
    if not session.get('admin') :
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login.html")
    
    else:
        feed = db.session.query(User, Todo).\
        filter(Todo.user_id == User.id).order_by(Todo.sno.desc()).all()
        return render_template("table.html",feed=feed)

@app.route("/table/users",methods=['GET', 'POST'])
def user():

    if session.get('admin') :
        user = User.query.all()
        
        todo = db.session.query(User, Todo).\
        filter(Todo.user_id == User.id).order_by(Todo.date_created.desc()).all()
        return render_template('user.html', user=user,todo=todo )
    else:
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login.html")

@app.route("/update/user/<id>", methods=['GET', 'POST'])
def update_user(id):
    if not session.get('admin') :
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login.html")
    else:
        user = User.query.all()
        todo = db.session.query(User, Todo).\
        filter(Todo.user_id == User.id).order_by(Todo.date_created.desc()).all()
    
        if request.method=="POST":
            name = request.form.get("name").lower()
            email = request.form.get("email")
            password = request.form.get("password")
            phone = request.form.get("phone")
            
            serv = db.session.query(User).filter_by(id=id).first()
            useru = User.query.filter_by(id = id).first()
            useru.name = name
            useru.email = email
            useru.password = password
            useru.phone= phone
            db.session.commit()
            flash('Successfully Updated!','success')
            return redirect(url_for('user'))

        else:
            serv = User.query.filter(User.id == id).first()
            return render_template("upus.html", todo=todo,user=user,serv=serv)

@app.route("/add/user", methods=['GET', 'POST'])
def adduser():
    
    if not session.get('admin') :
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login.html")
    else:
        user = User.query.all()
        todo = db.session.query(User, Todo).\
        filter(Todo.user_id == User.id).order_by(Todo.date_created.desc()).all()
        
        if request.method == "POST":
            name = request.form.get("name").lower()
            email = request.form.get("email")
            password = request.form.get("password")
            phone = request.form.get("phone")

            user = User.query.filter_by(email=email).first()
            if not user:
            # Creat new record
                usere = User(name=name, email=email,password=password, phone=phone)

                db.session.add(usere)
                db.session.commit()
                flash('Successfully added!','success')
                return redirect(url_for('user'))

            else:
                flash('Username or Email already exists','danger')
                return redirect (url_for(('adduser')))
 
        return render_template('addus.html', user=user,todo=todo)

@app.route("/delete/user/<id>", methods=['GET', 'POST'])
def delete_user(id):

    if not session.get('admin') :
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login.html")
    
    else:
       
        duser = User.query.filter(User.id==id).first()

        db.session.delete(duser)
        db.session.commit()
        flash('Successfully Deleted!','success')
        return redirect(url_for('user'))

@app.route("/delete/dairy/<int:sno>", methods=['GET', 'POST'])
def delete_ord(sno):
    if not session.get('admin') :
        session.clear()
        flash('Unauthorized access login correctly! ','danger')
        return render_template("login.html")
    
    else:
        fe = Todo.query.filter(Todo.sno == sno).first()

        db.session.delete(fe)
        db.session.commit()
        flash('Successfully Deleted!','success')
        return redirect(url_for('table'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, port=8000)