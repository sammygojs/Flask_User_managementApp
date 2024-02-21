from flask import Flask, flash ,render_template,request,redirect,session,send_file,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from io import BytesIO
from reportlab.pdfgen import canvas
app=Flask(__name__)
app.config["SECRET_KEY"]='65b0b774279de460f1cc5c92'
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///ums.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]='filesystem'
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)


#User class
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    fname=db.Column(db.String(255), nullable=False)
    lname=db.Column(db.String(255), nullable=False)
    email=db.Column(db.String(255), nullable=False)
    username=db.Column(db.String(255), nullable=False)
    edu=db.Column(db.String(255), nullable=False)
    password=db.Column(db.String(255), nullable=False)
    status=db.Column(db.Integer,default=0, nullable=False)

    def serialize(self):
        return {"id": self.id,
                "fname": self.fname,
                "lname": self.lname,
                "email": self.email}

    def __repr__(self):
        return f'User("{self.id}","{self.fname}","{self.lname}","{self.email}","{self.edu}","{self.username}","{self.status}")'

# create admin Class
class Admin(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(255), nullable=False)
    password=db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'Admin("{self.username}","{self.id}")'

# create product Class
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Product(id={self.id}, pname='{self.pname}', price={self.price})>"
    
    def serialize(self):
        return {
            "id": self.id,
            "pname": self.pname,
            "price": self.price,
        }

class Cart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Cart(cart_id={self.cart_id}, user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity})"

    def serialize(self):
        return {
            'cart_id': self.cart_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'quantity': self.quantity
        }

# admin=Admin(username='admin',password=bcrypt.generate_password_hash('admin',10))
# mock_products = [
#     Product(pname='Product1', price=19.99, img='product1.jpg'),
#     Product(pname='Product2', price=29.99, img='product2.jpg'),
#     Product(pname='Product3', price=14.99, img='product3.jpg'),
#     Product(pname='Product4', price=24.99, img='product4.jpg'),
#     Product(pname='Product5', price=34.99, img='product5.jpg'),
# ]
    
mock_carts = [
    Cart(user_id=1, product_id=1, quantity=2),
    Cart(user_id=1, product_id=2, quantity=1),
    Cart(user_id=2, product_id=3, quantity=3),
    Cart(user_id=2, product_id=43, quantity=1)
]



#create table
with app.app_context():
    # db.create_all()
    # db.drop_all()
    # cartNode = db.session.query(Cart).filter_by(product_id=43).first()
    # print(cartNode)
    # cart_to_delete = db.session.query(Cart).filter_by(cart_id=43).first()
    # print(cart_to_delete)
    # admin = Admin(username="admin",password="admin")
    # pw_hash = bcrypt.generate_password_hash("admin", 10).decode('utf-8') 
    # admin = Admin(username="admin",password=pw_hash)
    # db.session.add(admin)
    # admins=Admin().query.filter_by(username="admin").first()
    # print(admins)
    # print(bcrypt.check_password_hash(admins.password, 'admin'))
    # Admin().query.delete()
    # print(Admin().query.all())
    # adminToBeDel = db.session.query(Admin).filter_by(id=2).first()
    # Admin.query.filter_by(id=2).delete
    # db.session.delete(cart_to_delete)
    # db.session.commit()
    # print(cart_to_delete)
    # print(db.session.query(Cart).filter_by(product_id=1).all())
    # db.session.commit()
    # for cart in mock_carts:
    #     db.session.add(cart)
    
    # db.session.add(admin)
    db.session.commit()

    # Delete all rows from the User table
    # db.session.query(Product).delete

    # # Commit the changes to the database
    # db.session.commit()
    # print(db.session.query(Admin).all())

#main index login
@app.route('/')
def index():
    return render_template('index.html',title="")

# admin login
@app.route('/admin',methods=["POST","GET"])
def adminIndex():
    # chect the request is post or not
    if request.method == 'POST':
        # get the value of field
        username = request.form.get('username')
        password = request.form.get('password')
        # check the value is not empty
        if username=="" and password=="":
            flash('Please fill all the field','danger')
            return redirect('/admin')
        else:
            # login admin by username 
            admins=Admin().query.filter_by(username=username).first()
            if admins and bcrypt.check_password_hash(admins.password, password):
                session['admin_id']=admins.id
                session['admin_name']=admins.username
                flash('Login Successfully','success')
                return redirect('/admin/dashboard')
            else:
                flash('Invalid Email and Password','danger')
                return redirect('/admin')
    else:
        return render_template('admin/index.html',title="Admin Login")

# admin Dashboard
@app.route('/admin/dashboard')
def adminDashboard():
    if not session.get('admin_id'):
        return redirect('/admin')
    totalUser=User.query.count()
    totalApprove=User.query.filter_by(status=1).count()
    NotTotalApprove=User.query.filter_by(status=0).count()
    return render_template('admin/dashboard.html',title="Admin Dashboard",totalUser=totalUser,totalApprove=totalApprove,NotTotalApprove=NotTotalApprove)

# admin logout
@app.route('/admin/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/admin')
    if session.get('admin_id'):
        # session['admin_id']=None
        # session['admin_name']=None
        for key in list(session.keys()):
            session.pop(key)
        return redirect('/')

#admin approve user
@app.route('/admin/approve-user/<int:id>')
def adminApprove(id):
    if not session.get('admin_id'):
        return redirect('/admin')
    User().query.filter_by(id=id).update(dict(status=1))
    db.session.commit()
    flash('Approve Successfully','success')
    return redirect('/admin/get-all-user')
    # return render_template('admin/all-user.html',title='Approve User',users=users)

# admin get all user 
@app.route('/admin/get-all-user', methods=["POST","GET"])
def adminGetAllUser():
    if not session.get('admin_id'):
        return redirect('/admin')
    if request.method== "POST":
        search=request.form.get('search')
        users=User.query.filter(User.username.like('%'+search+'%')).all()
        return render_template('admin/all-user.html',title='Approve User',users=users)
    else:
        users=User.query.all()
        return render_template('admin/all-user.html',title='Approve User',users=users)
    
# change admin password
@app.route('/admin/change-admin-password',methods=["POST","GET"])
def adminChangePassword():
    admin=Admin.query.get(1)
    if request.method == 'POST':
        username=request.form.get('username')
        password=request.form.get('password')
        if username == "" or password=="":
            flash('Please fill the field','danger')
            return redirect('/admin/change-admin-password')
        else:
            Admin().query.filter_by(username=username).update(dict(password=bcrypt.generate_password_hash(password,10)))
            db.session.commit()
            flash('Admin Password update successfully','success')
            return redirect('/admin/change-admin-password')
    else:
        return render_template('admin/admin-change-password.html',title='Admin Change Password',admin=admin)

#admin add user
@app.route('/admin/add-user',methods=["GET","POST"])
def addUser():
    if request.method=="GET":
        return render_template("admin/addUser.html")
    else:
        # get all input field name
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        username=request.form.get('username')
        edu=request.form.get('edu')
        password=request.form.get('password')
        # check all the field is filled are not
        if fname =="" or lname=="" or email=="" or password=="" or username=="" or edu=="":
            flash('Please fill all the field','danger')
            return redirect('/admin/add-user')
        else:
            is_email=User().query.filter_by(email=email).first()
            if is_email:
                flash('Email already Exist','danger')
                return redirect('/admin/add-user')
            else:
                hash_password=bcrypt.generate_password_hash(password,10)
                user=User(fname=fname,lname=lname,email=email,password=hash_password,edu=edu,username=username)
                db.session.add(user)
                db.session.commit()
                flash('Account has been created but you have to approve it to activate it','success')
                return redirect('/admin/add-user') 

#admin add product
@app.route('/admin/add-product',methods=["GET","POST"])
def addproduct():
    if request.method=="GET":
        return render_template("admin/addProduct.html")
    else:
        pname=request.form.get('pname')
        price=request.form.get('price')
        if pname =="" or price=="":
            flash('Please fill all the field','danger')
            return redirect('/admin/add-product')
        else:
            is_product=Product().query.filter_by(pname=pname).first()
            if is_product:
                flash('Product name already Exist','danger')
                return redirect('/admin/add-product')
            else:
                product = Product(pname=pname,price=price)
                db.session.add(product)
                db.session.commit()
                flash('Product has been created','success')
                return redirect('/admin/add-product')
            
# user dashboard
@app.route('/admin/changeUserPassword/<int:user_id>',methods=['POST','GET'])
def changeUserPassword(user_id):
    userEntity = User().query.filter_by(id=user_id).first()
    if request.method=="GET":
        return render_template("admin/user-change-password.html",users=userEntity)
    else:
        email=request.form.get('email')
        password=request.form.get('password')
        if email == "" or password == "":
            flash('Please fill the field','danger')
            return redirect('/admin/changeUserPassword/'+str(user_id))
        else:
            users=User.query.filter_by(email=email).first()
            if users:
               hash_password=bcrypt.generate_password_hash(password,10)
               User.query.filter_by(email=email).update(dict(password=hash_password))
               db.session.commit()
               flash('Password Change Successfully','success')

               return redirect('/admin/changeUserPassword/'+str(user_id))
            else:
                flash('Invalid Email','danger')
                return redirect('/admin/changeUserPassword/'+str(user_id))
            

#---------------------user area---------------------
# user dashboard
@app.route('/user/dashboard')
def userDashboard():
    if not session.get('user_id'):
        return redirect('/user')
    if session.get('user_id'):
        id=session.get('user_id')
        users=User().query.filter_by(id=id).first()
        # usersList=User.query.all()
        products=Product().query.all()
        # print(products)
        # if(session.get('cart')):
        #     cartSize = session['cart']
        # else:
        #     cartSize=[]
        # print(cartSize,type(cartSize))
        # print('Cart size: ',len(cartSize))

        user_data.append({
        'id': users.id,
        'firstName': users.fname,
        'lastName': users.lname,
        'email': users.email
    })
        
        return render_template('user/dashboard.html',title="User Dashboard",users=users,productsList=products)

@app.route('/user',methods=["POST","GET"])
def userIndex():
    if  session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method=="POST":
        # get the name of the field
        email=request.form.get('email')
        password=request.form.get('password')
        # check user exist in this email or not
        users=User().query.filter_by(email=email).first()
        if users and bcrypt.check_password_hash(users.password,password):
            # check the admin approve your account are not
            is_approve=User.query.filter_by(id=users.id).first()
            # first return the is_approve:
            if is_approve.status == 0:
                flash('Your Account is not approved by Admin','danger')
                return redirect('/user')
            else:
                session['user_id']=users.id
                session['username']=users.username
                flash('Login Successfully','success')
                return redirect('/user/dashboard')
        else:
            flash('Invalid Email and Password','danger')
            return redirect('/user')
    else:
        return render_template('user/index.html',title="User Login")

#user register
@app.route('/user/signup',methods=["POST","GET"])
def userSignup():
    if request.method=='POST':
        # get all input field name
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        username=request.form.get('username')
        edu=request.form.get('edu')
        password=request.form.get('password')
        # check all the field is filled are not
        if fname =="" or lname=="" or email=="" or password=="" or username=="" or edu=="":
            flash('Please fill all the field','danger')
            return redirect('/user/signup')
        else:
            is_email=User().query.filter_by(email=email).first()
            if is_email:
                flash('Email already Exist','danger')
                return redirect('/user/signup')
            else:
                hash_password=bcrypt.generate_password_hash(password,10)
                user=User(fname=fname,lname=lname,email=email,password=hash_password,edu=edu,username=username)
                db.session.add(user)
                db.session.commit()
                flash('Account Create Successfully Admin Will approve your account in 10 to 30 mint ','success')
                return redirect('/user') 
    else:
        return render_template('user/signup.html',title="User Signup")

# user logout
@app.route('/user/logout')
def userLogout():
    if not session.get('user_id'):
        return redirect('/user')

    if session.get('user_id'):
        # session['user_id'] = None
        # session['username'] = None
        # session['cart'] = None
        for key in list(session.keys()):
            session.pop(key)
        return redirect('/user')

@app.route('/user/change-password',methods=["POST","GET"])
def userChangePassword():
    if not session.get('user_id'):
        return redirect('/user/')
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')
        if email == "" or password == "":
            flash('Please fill the field','danger')
            return redirect('/user/change-password')
        else:
            users=User.query.filter_by(email=email).first()
            if users:
               hash_password=bcrypt.generate_password_hash(password,10)
               User.query.filter_by(email=email).update(dict(password=hash_password))
               db.session.commit()
               flash('Password Change Successfully','success')

               return redirect('/user/change-password')
            else:
                flash('Invalid Email','danger')
                return redirect('/user/change-password')
    else:
        if session.get('user_id'):
            id=session.get('user_id')
            users=User().query.filter_by(id=id).first()
            return render_template('user/change-password.html',title="Change Password",users=users)
        else:
            return render_template('user/change-password.html',title="Change Password")

# user update profile
@app.route('/user/update-profile', methods=["POST","GET"])
def userUpdateProfile():
    if not session.get('user_id'):
        return redirect('/user')
    if session.get('user_id'):
        id=session.get('user_id')
    users=User.query.get(id)
    if request.method == 'POST':
        # get all input field name
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        username=request.form.get('username')
        edu=request.form.get('edu')
        if fname =="" or lname=="" or email=="" or username=="" or edu=="":
            flash('Please fill all the field','danger')
            return redirect('/user/update-profile')
        else:
            session['username']=None
            User.query.filter_by(id=id).update(dict(fname=fname,lname=lname,email=email,edu=edu,username=username))
            db.session.commit()
            session['username']=username
            flash('Profile update Successfully','success')
            return redirect('/user/dashboard')
    else:
        return render_template('user/update-profile.html',title="Update Profile",users=users)



# -------------printing methods------------
user_data = []
@app.route('/generate-pdf', methods=['GET'])
def generate_pdf():
    # if request.method == 'POST':
    #     # Retrieve user input from the form
    #     title = request.form.get('title')
    #     author = request.form.get('author')
    #     publication_year = request.form.get('publication_year')
         
        # Validate and store the user input
        # if title and author and publication_year:
    # user_data.append({
    #     'title': "title",
    #     'author': "author",
    #     'publication_year': "publication_year"
    # })
 
    pdf_file = generate_pdf_file()
    return send_file(pdf_file, as_attachment=True, download_name='user_details.pdf')
 
def generate_pdf_file():
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
 
    # Create a PDF document
    p.drawString(100, 750, "User details")
 
    y = 700
    for user in user_data:
        p.drawString(100, y, f"User id: {user['id']}")
        p.drawString(100, y - 20, f"First Name: {user['firstName']}")
        p.drawString(100, y - 40, f"Last Name: {user['lastName']}")
        y -= 60
 
    p.showPage()
    p.save()
 
    buffer.seek(0)
    return buffer

# --------------Product------------------
@app.route('/Product/<int:productId>', methods=['GET','POST','DELETE'])
def data(productId):
    if request.method=='POST':
        userId=session.get('user_id')
        # userDetails=User().query.filter_by(id=userId).first()
        # products = Product().query.all()
        # productToBeAdded = Product().query.filter_by(id=productId).first()
        # cartNode = db.session.query(Cart).filter_by(product_id=productId).all()
        cart_to_update = Cart().query.filter_by(user_id=userId,product_id=productId).first()
        # cart_to_update = db.session.query(Cart).filter_by(product_id=productId).first()
        print("cart_to_update",cart_to_update)
        # print("cartNode",cartNode)
        # usersList=User.query.all()
        # if not session.get('cart'):
        #     session['cart'] = [{"product": productToBeAdded.serialize(), "count":1}]
        #     cartNode = Cart(user_id=userId, product_id=productId, quantity=1)
        #     db.session.add(cartNode)
        #     # return render_template('user/dashboard.html',title="User Dashboard",users=userDetails,productsList=products)
        #     return redirect(url_for('userIndex')) 
        # else:
        #     productList = session['cart']

        #     f=0
        #     for item in productList:
        #         if item['product']['id'] == productId:
        #             item['count'] += 1
        #             f=1
    
        #     if f==0:
        #         # print("new product")
        #         new_product = {
        #         'count': 1,
        #         'product': productToBeAdded.serialize()  
        #         }
        #         productList.append(new_product)

        #     session['cart'] = productList
        #     cartNode = db.session.query(Cart).filter_by(product_id=productId).first()
        #     if cartNode:
                
        #     else:
        #         cartNode = Cart(user_id=userId, product_id=productId, quantity=1)
        #         db.session.add(cartNode)

        #     # return render_template('user/dashboard.html',title="User Dashboard",users=userDetails,productsList=products)
        #     # return redirect('http://localhost:5000/user/dashboard')   
        #     return redirect(url_for('userIndex')) 
        # with app.app_context():
    # db.create_all()
        
        # cartNode = Cart.query.filter_by(product_id=productId).all()
        if cart_to_update:
            cart_to_update.quantity+=1
            # print(cart_to_update.quantity)
            #if product exists in cart db -> increment the cart value
            # cartToBeAdded = cartNode.serialize()
            # cartToBeAdded['quantity'] +=1
            # print("carToBeAdded",cartToBeAdded)
            # print(type(cartToBeAdded))
            # newCart = Cart(cartToBeAdded['cart_id'],cartToBeAdded['user_id'],cartToBeAdded['product_id'],cartToBeAdded['quantity'])
            db.session.add(cart_to_update)
            db.session.commit()
            return redirect(url_for('userIndex')) 
        else:
            #product not in cart db -> create a new value
            print("new cart")
            cartToBeAdded = Cart(user_id=userId, product_id=productId, quantity=1)
            print(cartToBeAdded)
            db.session.add(cartToBeAdded)
            db.session.commit()
            return redirect(url_for('userIndex')) 
    else:
        product = Product().query.filter_by(id=productId).first()
        return render_template('user/product.html',product=product)

@app.route('/cart',methods=['GET','POST'])
def CartIndex():
        userId=session.get('user_id')
        print("userId",userId)
        cartItems = Cart().query.filter_by(user_id=userId).all()
        productList = []
        for cart in cartItems:
            productList.append(Product().query.filter_by(id=cart.product_id).first())
        print("cartItems",cartItems)
        print("productList",productList)
        # return '<h1>Hello</h1>'
        # return render_template("user/cart.html", cartData=cartItems, productList=productList)
        cartSize = len(cartItems)
        return render_template("user/cart.html", data = zip(cartItems,productList), cartSize=cartSize)
        # if not session.get('cart'):
        #     return render_template("user/cart.html")
        # else:
        #     cart_data = session.get('cart')
        #     return render_template("user/cart.html", cartData=cart_data)

@app.route('/IncrCart/<int:productId>',methods=['GET','POST'])
def IncrementCartValue(productId):
    if request.method=='POST':
        # productList = session['cart']

        # for item in productList:
        #     if item['product']['id'] == productId:
        #         item['count'] += 1

        # session['cart'] = productList
        # cart_data = session.get('cart')
        # return render_template('user/cart.html', cartData=cart_data)
        userId=session.get('user_id')
        cart_to_update = Cart().query.filter_by(user_id=userId,product_id=productId).first()
        # print("cart_to_update",cart_to_update)
        # db.session.delete(cart_to_update)
        cart_to_update.quantity+=1
        # print("cart_to_update",cart_to_update)
        db.session.add(cart_to_update)
        db.session.commit()
        return redirect(url_for('CartIndex')) 


@app.route('/DecrCart/<int:productId>',methods=['GET','POST'])
def DecrementCartValue(productId):
    if request.method=='POST':
        userId=session.get('user_id')
        cart_to_update = Cart().query.filter_by(user_id=userId,product_id=productId).first()
        # print("cart_to_update",cart_to_update)
        # db.session.delete(cart_to_update)
        if(cart_to_update.quantity==1):
            db.session.delete(cart_to_update)
            # cart_to_update.quantity-=1
            # db.session.add(cart_to_update)
            db.session.commit()
            flash('Item Deleted','danger')
            return redirect(url_for('CartIndex'))
        cart_to_update.quantity-=1
        # print("cart_to_update",cart_to_update)
        db.session.add(cart_to_update)
        db.session.commit()
        # flash()
        return redirect(url_for('CartIndex')) 
        # productList = session['cart']

        # for item in productList:
        #     if item['product']['id'] == productId:
        #         if(item['count']==1):
        #             flash('Item Deleted','danger')
        #             productList=remove_product_by_id(productId)
        #         else:
        #             item['count'] -= 1

        # session['cart'] = productList
        # # cart_data = session.get('cart')
        # return redirect(url_for('Cart'))
        # # return render_template('user/cart.html', cartData=cart_data)
            
# def remove_product_by_id(product_id):
#     data = session['cart']
#     data = [item for item in data if item['product']['id'] != product_id]
#     return data

@app.route('/admin/add-product', methods=['GET'])
def addProduct():
    if request.method=='GET':
        return render_template('admin/addProduct.html')

if __name__=="__main__":
    app.run(debug=True)