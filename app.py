from flask import Flask, render_template, redirect, url_for, session, request, make_response
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
def view_profile():
    try:
        x.disable_cache()  # Prevent caching so you cannot go back to the profile page after logout
        name = request.cookies.get("me")  # Retrieve the cookie
        
        if not name:  # Cookie is missing or invalid
            response = make_response()
            response.status_code = 303
            response.headers["Location"] = "/login"
            return response
        
        # Render the profile template
        return render_template("profile.html", name=name)
    
    except Exception as ex:
        if len(ex.args) >= 2:  # Handle your custom exception
            response = make_response({"error": ex.args[0]})
            response.status_code = ex.args[1]
            return response
        else:  # Handle other Python exceptions
            response = make_response({"error": "System under maintenance. Please try again."})
            response.status_code = 500
            return response

    finally:
        pass  # Cleanup actions if needed