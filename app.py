from flask import Flask, render_template, redirect, url_for, session, request, make_response, flash
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import x
import uuid
import time

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'  # or 'redis', etc.
Session(app)


##############################
##############################
##############################

def _________GET_________(): pass

##############################
##############################
@app.get("/")
def view_index():
    test_variable = "test"
    return render_template("view_index.html", test_variable=test_variable)

##############################
@app.get("/signup")
@x.no_cache
def view_signup():  
    ic(session)
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))         
    return render_template("view_signup.html", x=x, title="Signup")

##############################
@app.get("/login")
@x.no_cache
def view_login():  
    # ic("#"*20, "VIEW_LOGIN")
    ic(session)
    # print(session, flush=True)  
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))         
    return render_template("view_login.html", x=x, title="Login", message=request.args.get("message", ""))

@app.get("/reset_password")
def reset_request():
    return render_template("view_reset_password.html", title="Reset Password", x=x)

##############################
@app.get("/customer")
@x.no_cache
def view_customer():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    return render_template("view_customer.html", user=user)

##############################
@app.get("/partner")
@x.no_cache
def view_partner():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    return response

##############################
@app.get("/admin")
@x.no_cache
def view_admin():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    if not "admin" in user.get("roles", ""):
        return redirect(url_for("view_login"))
    return render_template("view_admin.html")

##############################
@app.get("/restaurant")
@x.no_cache
def view_restaurant():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    user = session.get("user")
    if not "restaurant" in user.get("roles", ""):
        return redirect(url_for("view_login"))
    return render_template("view_restaurant.html")

##############################
@app.get("/choose-role")
@x.no_cache
def view_choose_role():
    if not session.get("user", ""): 
        return redirect(url_for("view_login"))
    if not len(session.get("user").get("roles")) >= 2:
        return redirect(url_for("view_login"))
    user = session.get("user")
    return render_template("view_choose_role.html", user=user, title="Choose role")

##############################
@app.get("/profile")
@x.no_cache
def view_profile():
    try:
        name = request.cookies.get("me")
        
        if not name:
            response = make_response()
            response.status_code = 303
            response.headers["Location"] = "/login"
            return response
        
        return render_template("profile.html", name=name)
    
    except Exception as ex:
        if len(ex.args) >= 2:
            response = make_response({"error": ex.args[0]})
            response.status_code = ex.args[1]
            return response
        else:
            response = make_response({"error": "System under maintenance. Please try again."})
            response.status_code = 500
            return response

    finally:
        pass

##############################
##############################
##############################

def _________POST_________(): pass

##############################
##############################
##############################

@app.post("/users")
@x.no_cache
def signup():
    try:
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()
        hashed_password = generate_password_hash(user_password)
        user_role = request.form.get("user_role")

        role_mapping = {
            "customer": "83a69f25-a755-11ef-a5b9-0242ac120002",
            "restaurant": "83a6a87e-a755-11ef-a5b9-0242ac120002"
        }

        if user_role not in role_mapping:
            raise x.CustomException("Invalid role selected", 400)
        
        role_pk = role_mapping[user_role]
        
        user_pk = str(uuid.uuid4())
        user_created_at = int(time.time())
        user_deleted_at = 0
        user_blocked_at = 0
        user_updated_at = 0
        user_verified_at = 0
        user_verification_key = str(uuid.uuid4())

        db, cursor = x.db()
        q = '''INSERT INTO users (
                user_pk, user_name, user_last_name, user_email, user_password, 
                user_created_at, user_deleted_at, user_blocked_at, user_updated_at, 
                user_verified_at, user_verification_key
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        cursor.execute(q, (
            user_pk, user_name, user_last_name, user_email, hashed_password, 
            user_created_at, user_deleted_at, user_blocked_at, user_updated_at, 
            user_verified_at, user_verification_key
        ))
        
        q_users_roles = """
            INSERT INTO users_roles (user_role_user_fk, user_role_role_fk)
            VALUES (%s, %s)
            """
        cursor.execute(q_users_roles, (user_pk, role_pk))
        
        x.send_verify_email(user_email, user_verification_key)
        db.commit()

        print(f"User created for user_pk: {user_pk}") 
        return redirect(url_for("view_login", message="Account created, please verify your email to login")), 201
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            if "users.user_email" in str(ex): 
                toast = render_template("___toast.html", message="email not available")
                return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400
            return f"""<template mix-target="#toast" mix-bottom>System upgrating</template>""", 500        
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance</template>""", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.post("/login")
def login():
    try:
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()

        db, cursor = x.db()

        user_query = """SELECT * FROM users WHERE user_email = %s"""
        cursor.execute(user_query, (user_email,))
        user_row = cursor.fetchone()

        if not user_row:
            toast = render_template("___toast.html", message="User not registered")
            return f"""<template mix-target="#toast">{toast}</template>""", 400

        if user_row["user_deleted_at"] != 0:
            toast = render_template("___toast.html", message="Account has been deleted")
            return f"""<template mix-target="#toast">{toast}</template>""", 403

        if user_row["user_verified_at"] == 0:
            toast = render_template("___toast.html", message="User not verified")
            return f"""<template mix-target="#toast">{toast}</template>""", 403

        if not check_password_hash(user_row["user_password"], user_password):
            toast = render_template("___toast.html", message="Invalid credentials")
            return f"""<template mix-target="#toast">{toast}</template>""", 401

        role_query = """SELECT * FROM users_roles 
                        JOIN roles ON role_pk = user_role_role_fk
                        WHERE user_role_user_fk = %s"""
        cursor.execute(role_query, (user_row["user_pk"],))
        role_rows = cursor.fetchall()

        roles = [row["role_name"] for row in role_rows]

        user = {
            "user_pk": user_row["user_pk"],
            "user_name": user_row["user_name"],
            "user_last_name": user_row["user_last_name"],
            "user_email": user_row["user_email"],
            "roles": roles
        }
        ic(user)
        session["user"] = user

        if len(roles) == 1:
            return f"""<template mix-redirect="/{roles[0]}"></template>"""
        return f"""<template mix-redirect="/choose-role"></template>"""
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast">{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrading</template>", 500
        return "<template>System under maintenance</template>", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
@app.post("/forgot-password")
def forgot_password():
    try:
        user_email = request.form.get("user_email")
        if not user_email:
            raise x.CustomException("Email is required", 400)

        # Fetch user by email
        db, cursor = x.db()
        q = "SELECT user_pk FROM users WHERE user_email = %s AND user_deleted_at = 0"
        cursor.execute(q, (user_email,))
        user = cursor.fetchone()

        if not user:
            raise x.CustomException("Email not found", 404)

        # Generate a reset token
        reset_token = str(uuid.uuid4())

        # Store the reset token in the database
        q = "UPDATE users SET user_verification_key = %s WHERE user_pk = %s"
        cursor.execute(q, (reset_token, user["user_pk"]))
        db.commit()

        # Send the reset email (pass only the reset token)
        x.send_reset_email(user_email, reset_token)

        return """<template mix-target="#toast" mix-bottom>Reset email sent.</template>""", 200

    except Exception as ex:
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        return """<template mix-target="#toast" mix-bottom>System error occurred.</template>""", 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

#The link is fucked
#Display message signup succesful please verify your email
#Display message make pretty email send
##############################
@app.post("/reset_password")
def update_password():
    try:
        user_pk = request.form.get("user_pk")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not user_pk or not new_password or not confirm_password:
            raise x.CustomException("All fields are required", 400)

        if new_password != confirm_password:
            raise x.CustomException("Passwords do not match", 400)

        # Hash the new password
        hashed_password = generate_password_hash(new_password)

        # Get the current epoch timestamp
        updated_at = int(time.time())

        # Update the user's password and updated_at in the database
        db, cursor = x.db()
        q = """
            UPDATE users 
            SET user_password = %s, user_updated_at = %s 
            WHERE user_pk = %s
        """
        cursor.execute(q, (hashed_password, updated_at, user_pk))
        db.commit()

        print(f"Password updated successfully for user_pk: {user_pk}")  # Debugging
        return redirect(url_for("view_login", message="Password updated, please login"))

    except Exception as ex:
        print(f"Error: {ex}")  # Debugging
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        return """<template mix-target="#toast" mix-bottom>System error occurred.</template>""", 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
@app.post("/delete-user")
def delete_user():
    try:
        user_pk = session.get("user", {}).get("user_pk")
        if not user_pk:
            raise x.CustomException("User not logged in", 403)

        deleted_at = int(time.time())

        db, cursor = x.db()
        q = """
            UPDATE users 
            SET user_deleted_at = %s 
            WHERE user_pk = %s
        """
        cursor.execute(q, (deleted_at, user_pk))
        db.commit()

        print(f"User soft-deleted successfully for user_pk: {user_pk}") 

        session.clear()

        print(f"User succesfully deleted for user_pk: {user_pk}") 
        return redirect(url_for("view_login", message="User succesfully deleted"))

    except Exception as ex:
        print(f"Error: {ex}")  # Debugging
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast">{toast}</template>""", ex.code
        return """<template mix-target="#toast">System error occurred.</template>""", 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




##############################
@app.post("/logout")
def logout():
    # ic("#"*30)
    # ic(session)
    session.pop("user", None)
    # session.clear()
    # session.modified = True
    # ic("*"*30)
    # ic(session)
    return redirect(url_for("view_login"))
    
##############################
##############################
##############################

def _________PUT_________(): pass

##############################
##############################
##############################


##############################
##############################
##############################

def _________BRIDGE_________(): pass

##############################
##############################
##############################

@app.get("/verify/<verification_key>")
@x.no_cache
def verify_user(verification_key):
    try:
        ic(verification_key)
        verification_key = x.validate_uuid4(verification_key)
        user_verified_at = int(time.time())

        db, cursor = x.db()
        q = """ UPDATE users 
                SET user_verified_at = %s 
                WHERE user_verification_key = %s"""
        cursor.execute(q, (user_verified_at, verification_key))
        if cursor.rowcount != 1: x.raise_custom_exception("cannot verify account", 400)
        db.commit()
        return redirect(url_for("view_login", message="User verified, please login"))

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): return ex.message, ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "Database under maintenance", 500        
        return "System under maintenance", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##################################
@app.get("/reset_password/<token>")
def reset_password(token):
    try:
        print(f"Token received: {token}")  # Debugging
        # Verify the reset token
        db, cursor = x.db()
        q = "SELECT user_pk FROM users WHERE user_verification_key = %s AND user_deleted_at = 0"
        cursor.execute(q, (token,))
        user = cursor.fetchone()

        print(f"User fetched: {user}")  # Debugging

        if not user:
            raise x.CustomException("Invalid or expired reset link", 400)

        # Render the reset password form
        return render_template("view_set_new_password.html", user_pk=user["user_pk"])

    except Exception as ex:
        print(f"Error: {ex}")  # Debugging
        if isinstance(ex, x.CustomException):
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code
        return """<template mix-target="#toast" mix-bottom>System error occurred.</template>""", 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()
