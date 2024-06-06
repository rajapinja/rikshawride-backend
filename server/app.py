from flask import Flask, request, jsonify, g, json, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt, decode_token
import jwt
import secrets
import bcrypt
import random
import time
from datetime import datetime, date, time, timedelta
from flask_cors import CORS
from mysqlconnect import DatabaseConnection
import requests
from user_roles import user_roles
from user_roles import insert_users_roles, user_already_exists, get_user_id, get_users_roles_role_id, get_role
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from flask_sqlalchemy import SQLAlchemy

#Swagger Stuff
from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)

CORS(app)
#CORS(app, resources={r"/api/*": {"origins": "http://localhost:19006"}})

# Register the blueprints ( )
app.register_blueprint(user_roles)
#app.register_blueprint(timer)

app.secret_key = secrets.token_hex(16) 

jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/rikshawride'
db = SQLAlchemy(app)
# Create a singleton database connection instance
connection = DatabaseConnection().get_connection()

# Get the current timestamp
current_timestamp = datetime.now()

# Format the timestamp as a string in MySQL acceptable format
mysql_timestamp = current_timestamp.strftime('%Y-%m-%d %H:%M:%S')
password_reset_tokens = {}


# Create an instance of the GPSApp class
#gps_app = GPSApp()

# Call the get_location() method on the GPSApp instance
#gps_app.get_location()


drivers = [
    {'driver_id': 1, 'name': 'John', 'vehicle_type': 'Sedan', 'location': (12.9716, 77.5946)},
    {'driver_id': 2, 'name': 'Alice', 'vehicle_type': 'SUV', 'location': (12.9824, 77.6631)},
    {'driver_id': 3, 'name': 'Bob', 'vehicle_type': 'Hatchback', 'location': (12.9870, 77.6040)}
]

#pip install alembic
#alembic init alembic - run once
#alembic revision --autogenerate -m "Create BlacklistToken table"
#alembic revision --autogenerate -m "Create BlacklistToken table"
#alembic upgrade head

# Define SQLAlchemy models
class BlacklistToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), unique=True, nullable=False)


# Define the unauthorized response handler
@jwt.unauthorized_loader
def unauthorized_response(callback):
    print('Unauthorized')
    return jsonify(message='Unauthorized'), 401

# Define the invalid token response handler
@jwt.invalid_token_loader
def invalid_token_response(callback):
    print('Invalid token')
    return jsonify(message='Invalid token'), 401

# Define the expired token response handler
@jwt.expired_token_loader
def expired_token_response(expired_token):
    print('Token has expired')
    return jsonify(message='Token has expired'), 401

#To get roles
@app.route('/api/roles', methods=['GET'])
def get_roles():
    """
    Get User Roles Endpoint
    ---
    tags:
      - Available Roles 
    get:
      summary: Retrieve user roles
      responses:
        200:
          description: User roles retrieved successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  userRoles:
                    type: array
                    items:
                      type: object
                      properties:
                        role:
                          type: string
        404:
          description: No roles found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
        500:
          description: An error occurred while retrieving roles
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
    """
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT role FROM roles")
        roles = cursor.fetchall()
        cursor.close()

        print(roles)

        if roles:
            return jsonify({"userRoles": roles}), 200
        else:
            return jsonify({"message": "No roles found"}), 404
        
    except Exception as e:
        error_message = str(e)  # Extract the error message from the exception        
        if "MySQL Connection not available" in error_message:
            return jsonify({"error": "MySQL Connection not available"}), 500
        else:
            return jsonify({"error": "An error occurred"}), 500
        

@app.route('/api/registration', methods=['POST'])
def registration():

    """
    User Registration Endpoint
    ---
    tags:
      - Player Registration
    post:
      summary: Register a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                userpassword:
                  type: string
                email:
                  type: string
                selectedRole:
                  type: string
      responses:
        200:
          description: Registration successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
        400:
          description: Registration failed or user already exists
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
      parameters:
        - in: body
          name: user_data
          required: true
          description: JSON object containing user registration data
          schema:
            type: object
            properties:
              username:
                type: string
              userpassword:
                type: string
              email:
                type: string
              selectedRole:
                type: string
    """

    data = request.get_json()

    # Extracting data from the request
    name = data['username']
    password = data['password']
    email = data['email']
    phone = data['phone']
    role = data['role']
        
    # Conditionally assign vehicleType based on the selected role
    if role == 'AutoOwner':
      vehicle_type = data.get('vehicleType')
    else:
      vehicle_type = None

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
   
    try:

        if user_already_exists(connection, name) :            
            return jsonify({'error': 'User already exists'}), 409 
        else:            
            cursor = connection.cursor()
            if vehicle_type is None:
                # If vehicle_type is None, exclude the vehicle_name column from the SQL statement
                sql_stmt = "INSERT INTO users (name, password, email, phone, role) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql_stmt, (name, password_hash, email, phone, role))
            else:
                # If vehicle_type is not None, include the vehicle_name column in the SQL statement
                sql_stmt = "INSERT INTO users (name, password, email, phone, role, vehicle_name) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql_stmt, (name, password_hash, email, phone, role, vehicle_type))   

            connection.commit()     

            user_id = get_user_id(connection, name)       
            #Insert password into password_history
            cursor.execute("INSERT INTO password_history (user_id, password_hash) VALUES (%s, %s)", (user_id, password_hash))
            
            connection.commit()
            cursor.close()
            #Call users_roles table to update with user roles from user_roles table
            sucess = insert_users_roles(connection, name, role)
            if sucess:              
                return jsonify({'message': 'Registration successful with '+sucess}), 200
            else:
                return jsonify({'error': 'Registration Failed with User and Role'}), 200  

    except Exception as e:      
        error_code = e.errno  # Get the MySQL error code
        if error_code == 1062:
            error_message = "Duplicate entry. User already exists."
        else:
            error_message = "An error occurred during registration."

        return jsonify({"error": error_message}), 400    


#User Login without password expiration logic
@app.route('/api/userlogin', methods=['POST'])
def userlogin():
    """
    User Login Endpoint
    ---
    tags:
      - Player Login
    post:
      summary: Authenticate user and generate access token
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                password:
                  type: string
      responses:
        200:
          description: Login successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                  user:
                    type: string
                  role:
                    type: string
                  accessToken:
                    type: string
        401:
          description: Invalid credentials
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
        404:
          description: User not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
      parameters:
        - in: body
          name: user_credentials
          required: true
          description: JSON object containing user credentials
          schema:
            type: object
            properties:
              username:
                type: string
              password:
                type: string
    """

    data = request.get_json()       
    user = data['username']
    password = data['password']

    try:
        cursor = connection.cursor()       
       # Fetch user data from the database based on the username
        cursor.execute('SELECT password FROM users WHERE name = %s', (user,))
        user_data = cursor.fetchone()       
        cursor.close()  
        print(user_data)

        if user_data[0] is not None:
            print(user_data)
            # Encode the user-entered password as bytes
            user_password_bytes = password.encode('utf-8')

            if user_data:
                stored_password_hash = user_data[0]
                stored_password_hash = stored_password_hash.encode('utf-8')
                #if pbkdf2_sha256.verify(password, stored_password_hash):
                if bcrypt.checkpw(user_password_bytes, stored_password_hash):
                    #get user_id by passing user to users table
                    user_id = get_user_id(connection, user)                   
                    print(user_id)
                    #get role_id by passing user_id to users_roles table
                    role_id = get_users_roles_role_id(connection, user_id)
                    print(role_id)
                    #get role from roles table by passing role_id
                    role = get_role(connection, role_id)
                    print(role)

                    access_token = generate_token_with_expiration(user_id)
                    #return jsonify(access_token=access_token), 200
                    print("access_token : ", access_token)

                    # Keep track of the token's JTI
                    jti = get_jti_from_token(encoded_token=access_token)

                    print("jti : ", jti)

                    insert_blacklist_token(jti)
                    # Save JTI to the database table
                    #blacklist_token = BlacklistToken(jti=jti)
                    #print('blacklist_token :',blacklist_token)

                   
                    # # Add the instance to the session
                    # db.session.add(blacklist_token)
                    # print('blacklist_token : add')
                    # # Commit the session to persist changes to the database
                    # db.session.commit()
                    # print('blacklist_token : commit')

                    return jsonify({
                        "message": "Login successful",
                        "user": user,
                        "role": role,
                        "accessToken":access_token,
                    }), 200                 

                else:
                    return jsonify({'error': 'Invalid credentials'}), 401
            else:
                return jsonify({'error': 'User not found'}), 404
        else:
            return jsonify({'error': 'User not found'}), 404                           

    except Exception as e:
        return jsonify({'error': str(e)}), 500 

# insert record in blacklisttoken table 
def insert_blacklist_token(jti):
    try:
        cursor = connection.cursor()
        sql_stmt ="INSERT INTO blacklisttoken(jti) VALUES (%s)"
        cursor.execute(sql_stmt,(jti,))
        connection.commit()
        cursor.close()

        print('token jti inserted successfully')

        return jsonify({"message":"token jti inserted successfully"})

    except Exception as e:
        return jsonify({'error': str(e)}), 500 
    

#Get User Deatails like username, email, created_at
# Placeholder function for getting user data
def get_user_data(username):
    # Replace this function with your actual logic to fetch user data from the database
    # Return a tuple (id, email, user_created_at) if the user exists, or None if not found
    try:
        with connection.cursor() as cursor:
            # Update the password in the users table
            cursor.execute('SELECT id, email, created_at FROM users WHERE username = %s', (username,))
            result = cursor.fetchone()

            if result:
                return result
        return None
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Function to send an email
def send_email(recipient_email, subject, message):
    # Replace these values with your email server configuration

   try:
    email_host = 'smtp.gmail.com'
    email_port = 587
    email_username = 'raja.pinja@gmail.com'
    email_password = 'tote nidu erbj cmhk'
    sender_email = 'raja.pinja@gmail.com'

    # Create a MIME object
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach the message to the MIME object
    msg.attach(MIMEText(message, 'plain'))

    # Establish a connection to the SMTP server
    #print("Attempting to connect to the SMTP server...")
    with smtplib.SMTP(email_host, email_port) as server:
      # server.set_debuglevel(1)  # Enable debugging
      # server.starttls()  # Upgrade the connection to TLS
      # server.login(email_username, email_password)
      # Debugging statements
     
      #server = smtplib.SMTP(email_host, email_port)
      server.starttls(context=ssl.create_default_context())
      #print("Successfully connected to the SMTP server.")
      server.login(email_username, email_password)
      #print("Successfully logged in.")
      server.sendmail(sender_email, recipient_email, msg.as_string())      

      #print(f"Email sent successfully to {recipient_email}")
   except Exception as e:
      print(f"Error sending email: {str(e)}")

def send_yahoo_email(recipient_email, subject, messageFrom):
    
  # Yahoo SMTP server settings
  smtp_server = 'smtp.mail.yahoo.com'
  smtp_port = 587  # Use 465 if SSL is required
  smtp_username = 'raja_pinja@yahoo.com'
  smtp_password = 'lvcqrprrgutrrijr'

  # Sender and recipient email addresses
  sender_email = 'raja_pinja@yahoo.com'
  recipient_email = 'raja.pinja@gmail.com'

  # Create the MIME object
  message = MIMEMultipart()
  message['From'] = sender_email
  message['To'] = recipient_email
  message['Subject'] = subject

  # Attach body to the message
  message.attach(MIMEText(messageFrom, 'plain'))

  try:
      # Connect to the SMTP server
      server = smtplib.SMTP(smtp_server, smtp_port)
      #print("Connected to SMTP server")

      server.starttls()  # Use this line for a secure connection
      #print("TLS started")

      # Login to the Yahoo email account
      server.login(smtp_username, smtp_password)
      #print("Logged in")

      # Send the email
      server.sendmail(sender_email, recipient_email, message.as_string())

      #print("Email sent successfully!")

  except Exception as e:
      print(f"Error sending email: {e}")

  finally:
      # Quit the SMTP server
      server.quit()


#Reset Password if its more than 15 days, since its creation
def update_password(username, new_password_hash):
    try:
        cursor = connection.cursor()
        # Update the password in the users table
        cursor.execute('UPDATE users SET password_hash = %s, created_at = CURRENT_TIMESTAMP WHERE username = %s', (new_password_hash, username))
        cursor.execute("UPDATE password_history SET password_hash = %s WHERE username = %s", (new_password_hash, username))
        connection.commit()
        cursor.close()
        return True
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# To get user's created_at value
def get_user_creation_timestamp(user_id):
    try:
        with connection.cursor() as cursor:
            # Execute the SELECT query
            cursor.execute('SELECT created_at FROM users WHERE id = %s', (user_id,))
            
            # Fetch the result
            result = cursor.fetchone()

            if result:
                # Assuming the 'created_at' field is in the first position of the result tuple
                return result[0]

        # Return a default timestamp if the user is not found (for demonstration purposes)
        return datetime.datetime(2022, 1, 1, 0, 0, 0)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#Reset Password Request
@app.route('/api/reset_password_request', methods=['POST'])
def reset_password_request():
    try:
        #print("Inside..reset_password_request ")
        data = request.get_json()
        username = data.get('username')

        #print("Inside..reset_password_request username :", username)
        # Validate email and check if the user exists
        user_data = get_user_data(username)
        if not user_data:
            return jsonify({'error': 'User not found'}), 404

        id, email, user_created_at = user_data
        #print("Inside..reset_password_request  id : , email: , user_created_at :",  id, email, user_created_at)

        user_created_at = get_user_creation_timestamp(id)
        print(" user_created_at :",  user_created_at)

        # Check if the user's password has expired (e.g., set expiration to 15 days)
        #expiration_time = user_created_at + datetime.timedelta(days=15)
        expiration_time = user_created_at + datetime.timedelta(days=45)
        #print("Expiration time:", expiration_time) 

        if datetime.datetime.utcnow() > expiration_time:
            # Password has expired, generate a reset token
            token = secrets.token_urlsafe(32)
            #print("Inside datetime.datetime.utcnow() > expiration_time token:", token) 

            password_reset_tokens[token] = {'user_id': id, 'expiration_time': datetime.datetime.now() + datetime.timedelta(hours=1)}
            #print("password_reset_tokens[token]:", password_reset_tokens[token]) 
            # Send the reset link to the user's email
            recipient_email = email  # Replace with the actual user's email
            subject = 'Password Reset'
            message = f'Click the following link to reset your password: https://4c8f-49-43-228-253.ngrok-free.app/api/reset_password_confirm?token={token}&username={username}'

            # Call the function to send the email
            #send_email(recipient_email, subject, message)
            send_yahoo_email(recipient_email, subject, message)

            return jsonify({'message': 'Password reset link sent successfully'})

        else:
           # Password has not expired, allow resetting on the screen
            return jsonify({'message': 'You can reset your password on the screen.'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# To handle password rest for email link   
@app.route('/api/reset_password_confirm', methods=['GET', 'POST'])
def reset_password_confirm():
  try:
    if request.method == 'GET':
        # Get the token and username from the query parameters
        token = request.args.get('token')
        username = request.args.get('username')

        # Render the password reset confirmation page with a form
        return render_template('reset_password_form.html', token=token, username=username)

    elif request.method == 'POST':
        # Handle POST request (process the submitted data)
        data = request.form
        token = data.get('token')
        username = data.get('username')
        new_password = data.get('new_password')

        # Verify the reset token
        if token not in password_reset_tokens:
            return jsonify({'error': 'Invalid or expired reset token'})

        # Check if the user exists
        user_id = get_user_id(connection, username)
        if user_id is None:
            return jsonify({'error': 'User not found'})

        # hash the Password using bcrypt
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        # Update the password in the users table       
        success = update_password(username, new_password_hash)

        if success:
            # Password successfully updated, remove the reset token
            del password_reset_tokens[token]
            return jsonify({'message': 'Password successfully updated'})

        else:
            return jsonify({'error': 'Failed to update password'})
        
  except Exception as e:
    print(f"Error in reset_password_confirm: {str(e)}")
    return jsonify({'error': 'Internal Server Error'}), 500

# To update expired password 
def update_reset_password(username, new_password_hash):          
  try:
      cursor = connection.cursor()
      # Update the password in the users table, and insert the password into password_history
      # Execute the SQL query to update the password hash and created_at timestamp
      # query = 'UPDATE users SET password_hash = %s, created_at = CURRENT_TIMESTAMP WHERE username = %s'
      # params = (new_password_hash, username)
      cursor.execute("UPDATE users SET password_hash = %s, registration_date = CURRENT_TIMESTAMP WHERE username = %s", (new_password_hash, username))
      cursor.execute("INSERT INTO password_history (username, password_hash) VALUES (%s, %s)", (username, new_password_hash))

      # cursor.execute(query, params)
      connection.commit()
      cursor.close()
      print("Password and created_at updated successfully.")

  except Exception as e:
      connection.rollback()
      #print("Error updating password and created_at:", e)     
      return jsonify({'error': str(e)}), 500 

def is_password_used(username, new_password_hash):
    cursor = connection.cursor()
    # Replace this with your actual database query to check if the password exists in the password history   
    cursor.execute("SELECT COUNT(*) FROM password_history WHERE username = %s AND password_hash = %s", (username, new_password_hash))
    return cursor.fetchone()[0] > 0
    
# Reset Password if password expired less than 45 days
@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()

        # Assuming you include the necessary data like username and token
        username = data.get('username')
        new_password = data.get('newPassword')
        confirm_password = data.get('confirmPassword')

        # Validate that the passwords match
        if new_password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400

        # You can add more password strength validation if needed

        # Encode the user-entered password as bytes        
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        # Call the reset_password function
       
        # Check if the new password has been used before
        if is_password_used(username, new_password_hash):
            print("Password has been used before. Please choose a different password.")
        else:
            # Update the password and password history
            update_reset_password(username, new_password_hash)
            print("Password reset successful.")

        return jsonify({'message': 'Password reset successful'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/logout', methods=['POST'])
@jwt_required()  # Require JWT for logout endpoint
def logout():
    # Retrieve JTI from the current token
    jti = get_jwt()['jti']

    # Check if JTI exists in the blacklist table
    if BlacklistToken.query.filter_by(jti=jti).first():
        return jsonify({"message": "Token already blacklisted"}), 401
    
    # Add the JTI to the blacklist
    blacklist_token = BlacklistToken(jti=jti)
    db.session.add(blacklist_token)
    db.session.commit()

    return jsonify({"message": "Successfully logged out"}), 200

def get_jti_from_token(encoded_token):
    decoded_token = decode_token(encoded_token)
    print("decoded_token : ",decoded_token)
    return decoded_token['jti']


@app.route('/api/fetchusertypes', methods=['GET'])
def get_usertypes():
    try:
        print("Inside -get_usertypes")
        cursor = connection.cursor(dictionary = True)
        sql = f"SELECT type_name FROM usertype"
        cursor.execute(sql)
        fetchedUsertypes = cursor.fetchall()
        cursor.close()

        print('fetchedUsertypes : ',fetchedUsertypes)
        return jsonify({"fetchedUsertypes": fetchedUsertypes}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/fetchvehicletypes', methods=['GET'])
def get_vehicletypes():
    try:
        print("Inside - get_vehicletypes")
        cursor = connection.cursor(dictionary = True)
        sql = f"SELECT type_name FROM vehicletype"
        cursor.execute(sql)
        fetchedVehicletypes = cursor.fetchall()
        cursor.close()

        print('fetchedVehicletypes : ',fetchedVehicletypes)
        return jsonify({"fetchedVehicletypes": fetchedVehicletypes}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/fetchautomodels', methods=['GET'])
def get_auto_models():
    try:
        print("Inside - get_auto_models")
        cursor = connection.cursor(dictionary = True)
        sql = f"SELECT model FROM auto_model"
        cursor.execute(sql)
        fetchedAutoModel = cursor.fetchall()
        cursor.close()

        print('fetchedAutoModel : ',fetchedAutoModel)
        return jsonify({"fetchedAutoModel": fetchedAutoModel}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# To fetch users, so that user can enter his vehicle details
@app.route('/api/fetchusers', methods=['GET'])
def get_user_ids():
    try:
        print("Inside - get_user_ids")
        cursor = connection.cursor(dictionary = True)
        sql = f"SELECT name, userid FROM users"
        cursor.execute(sql)
        fetchedUsers = cursor.fetchall()
        cursor.close()

        print('fetchedUsers : ',fetchedUsers)
        return jsonify({"fetchedUsers": fetchedUsers}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add auto   
@app.route('/api/addauto', methods=['POST'])
def add_auto_details():
    try:        
        data = request.get_json()
        VehicleNumber = data["vehicleRegNumber"]
        Model = data["selectedAutoModel"]
        RegistrationDate = data["registrationDate"]
        OwnerID = data["selectedUserId"]

        print('data :', data)

        cursor = connection.cursor()
        sql_stmt="INSERT INTO autorickshaws(OwnerID, VehicleNumber, Model, RegistrationDate) VALUES(%s, %s, %s, %s)"
        cursor.execute(sql_stmt, (OwnerID, VehicleNumber, Model, RegistrationDate))
        connection.commit()
        cursor.close()

        return jsonify({"message": "create record successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/find_ride', methods=['POST'])
def find_ride():
    # Get pickup and drop-off locations from the request
    pickup_location = request.json.get('pickup_location')
    dropoff_location = request.json.get('dropoff_location')

    # Use Google Maps API to identify current location and available nearby vehicles
    # Simulated response for demonstration
    nearby_vehicles = [
        {'driver_name': 'John', 'vehicle_type': 'Sedan', 'estimated_arrival_time': '5 minutes'},
        {'driver_name': 'Alice', 'vehicle_type': 'SUV', 'estimated_arrival_time': '7 minutes'},
        {'driver_name': 'Bob', 'vehicle_type': 'Hatchback', 'estimated_arrival_time': '10 minutes'}
    ]

    return {'nearby_vehicles': nearby_vehicles}

@app.route('/match_driver', methods=['POST'])
def match_driver():
    # Get user's pickup location from the request
    pickup_location = request.json.get('pickup_location')

    # Calculate distance between pickup location and drivers' locations
    available_drivers = []
    for driver in drivers:
        driver_location = driver['location']
        # Calculate distance (dummy calculation for demonstration)
        distance = abs(driver_location[0] - pickup_location[0]) + abs(driver_location[1] - pickup_location[1])
        if distance < 0.1:  # Consider drivers within 0.1 degrees (~11km) of pickup location
            available_drivers.append(driver)

    return {'available_drivers': available_drivers}

def get_current_location():
    # Simulate user's current location (latitude and longitude)
    # Replace these values with actual location retrieval logic
    latitude = 12.9716
    longitude = 77.5946
    return latitude, longitude

def find_nearby_vehicles():
    # Get user's current location
    latitude, longitude = get_current_location()

    # Google Maps Places API request to find nearby vehicles (using user's current location)
    places_api_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': f'{latitude},{longitude}',
        'radius': 1000,  # Define radius (in meters) to search for nearby places
        'type': 'car_rental',  # Adjust type according to the vehicles you're looking for
        'key': 'YOUR_GOOGLE_MAPS_API_KEY'
    }
    response = requests.get(places_api_url, params=params)
    data = response.json()

    # Extract relevant information about nearby vehicles
    nearby_vehicles = []
    if 'results' in data:
        for result in data['results']:
            vehicle_info = {
                'name': result['name'],
                'latitude': result['geometry']['location']['lat'],
                'longitude': result['geometry']['location']['lng'],
                'types': result['types']
            }
            nearby_vehicles.append(vehicle_info)

    return nearby_vehicles

class User:
    def __init__(self, name, pickup_location, destination):
        self.name = name
        self.pickup_location = pickup_location
        self.destination = destination

class Driver:
    def __init__(self, name):
        self.name = name

    def receive_notification(self, user):
        print(f"Notification: Ride request from {user.name} at {user.pickup_location}")
        # Simulate driver's decision to accept or reject the ride
        if random.choice([True, False]):
            print(f"{self.name} accepts the ride.")
            return True
        else:
            print(f"{self.name} rejects the ride.")
            return False

class Ride:
    def __init__(self, user, driver):
        self.user = user
        self.driver = driver

    def confirm_ride(self):
        if self.driver.receive_notification(self.user):
            print("Ride confirmed!")
            return True
        else:
            print("Ride rejected.")
            return False

    def start_ride(self):
        print("Ride started!")
        # Simulate ride experience with real-time tracking
        for i in range(10):  # Simulate 10 iterations for tracking
            time.sleep(1)  # Simulate real-time tracking interval
            print(f"{self.driver.name} is at location {random.randint(1, 100)}")
        print(f"{self.driver.name} has arrived at {self.user.pickup_location}")

    def complete_ride(self):
        print(f"{self.driver.name} has transported {self.user.name} to {self.user.destination}. Ride completed!")



# Example of generating a token with expiration
def generate_token_with_expiration(user_id):
    
    try:
        # Set the expiration time, e.g., 1 hour from now
        expiration = timedelta(hours=3)
        # Create a JWT access token with an expiration
        #print('user_id : ',user_id,)
        #print('expiration : ',expiration)
        access_token = create_access_token(identity=user_id, expires_delta=expiration)
        #print('access_token :', access_token)
        return access_token
    except Exception as e:
        # Handle exceptions and return an error response
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/swagger')  # This endpoint serves your Swagger specification
def generate_swagger_spec():
    # Generate the Swagger specification (JSON or YAML) for your API
    swag = swagger(app)
    swag['info']['title'] = 'Score Recorder'
    swag['info']['version'] = '1.0'
    return jsonify(swag)

# Swagger UI configuration
SWAGGER_URL = '/api/docs'  # URL for Swagger UI
API_URL = '/api/swagger'   # URL to your Swagger JSON or YAML file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Score Recorder"  # Specify your app name
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/')
def index():
    return 'Hello, Score Recorder!'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5011)
