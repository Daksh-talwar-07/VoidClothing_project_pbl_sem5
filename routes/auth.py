import re,secrets
from flask import (Blueprint,render_template,request,session,redirect,url_for,flash)
from werkzeug.security import generate_password_hash, check_password_hash
from models.customer import Customer
from extensions import db, limiter
from flask_login import login_user, logout_user, login_required
from store_config import STORE_NAME
from datetime import datetime, timedelta
from utils.email_service import send_email

auth = Blueprint("auth",__name__)


def valid_email(email):
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern,email) is not None

def valid_phone(phone):
    return phone.isdigit() and len(phone) == 10

def valid_name(name):
    return(
        2<=len(name)<=100
        and all(char.isalpha() or char in " .'-" for char in name)
    )

def valid_password (password):
    if len(password)<8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]",password):
        return False
    if not re.search(r"\d",password):
        return False

    return True


def generate_otp():
     return f"{secrets.randbelow(1000000):06d}"



def send_verification_email(customer, otp):

    html = f"""
    <div style="
        font-family: Arial, sans-serif;
        max-width: 600px;
        margin: auto;
        padding: 30px;
        color: #111;
    ">

        <h2>
            Welcome to {STORE_NAME}
        </h2>

        <p>
            Hi {customer.full_name},
        </p>

        <p>
            Thanks for creating your account.
            Use the verification code below to verify your email address.
        </p>

        <div style="
            margin: 30px 0;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
            text-align: center;
        ">

            <span style="
                font-size: 32px;
                font-weight: bold;
                letter-spacing: 8px;
            ">
                {otp}
            </span>

        </div>

        <p>
            This verification code expires in 10 minutes.
        </p>

        <p>
            If you didn't create this account, you can safely ignore this email.
        </p>

    </div>
    """

    return send_email(
        to=customer.email,
        subject=f"Verify your {STORE_NAME} account",
        html=html
    )

def send_password_reset_email(customer, otp):

    html = f"""
    <div style="
        font-family: Arial, sans-serif;
        max-width: 600px;
        margin: auto;
        padding: 30px;
        color: #111;
    ">

        <h2>
            Reset your {STORE_NAME} password
        </h2>

        <p>
            Hi {customer.full_name},
        </p>

        <p>
            We received a request to reset your password.
            Use the verification code below to continue.
        </p>

        <div style="
            margin: 30px 0;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
            text-align: center;
        ">

            <span style="
                font-size: 32px;
                font-weight: bold;
                letter-spacing: 8px;
            ">
                {otp}
            </span>

        </div>

        <p>
            This code expires in 10 minutes.
        </p>

        <p>
            If you did not request a password reset,
            you can safely ignore this email.
        </p>

    </div>
    """

    return send_email(
        to=customer.email,
        subject=f"Reset your {STORE_NAME} password",
        html=html
    )



@auth.route("/register",methods=["GET","POST"])
@limiter.limit("5 per minute")
def register():
    if request.method == "POST":
        
        full_name = request.form.get("full_name","").strip()
        email = request.form.get("email","").strip().lower()
        phone = request.form.get("phone","").strip()
        password = request.form.get("password","")

        if not full_name or not email or not phone or not password:
            flash ("Please fill all the fields." , "error")
            return redirect(url_for("auth.register"))

        if not valid_name(full_name):
            flash("Please enter a valid name.",
                  "error"
            )
            return redirect(url_for("auth.register"))

        if not valid_email(email):
                    flash("Please enter a valid email address.",
                          "error"
                    )
                    return redirect(url_for("auth.register"))

        if not valid_phone(phone):
                    flash("Please enter a valid 10-digit phone number.",
                          "error"
                    )
                    return redirect(url_for("auth.register"))

        if not valid_password(password):
            flash("Password must be at least 8 characters and contain"
                   "uppercase, lowercase and a number.",
                   "error"
            )
            return redirect(url_for("auth.register"))


        
        # Remove abandoned, never-verified sign-ups using this email/phone so the
        # person can simply register again (there is no "resend OTP" page).
        stale = Customer.query.filter(
            db.or_(Customer.email == email, Customer.phone == phone),
            Customer.email_verified == False
        ).all()
        for s in stale:
            db.session.delete(s)
        if stale:
            db.session.commit()

        existing_customer = Customer.query.filter_by(email=email).first()

        if existing_customer :
            flash("Email already registered.","error")
            return redirect(url_for("auth.register"))
        
        existing_phone = Customer.query.filter_by(phone=phone).first()

        if existing_phone:
            flash("Phone number already registered.", "error")
            return redirect(url_for("auth.register"))
        
        hashed_password = generate_password_hash(password)

        otp = generate_otp()

        otp_hash = generate_password_hash(otp)

        customer = Customer(
            full_name=full_name,
            email=email,
            phone=phone,
            password=hashed_password,

            email_verified=False,
            email_verification_otp_hash=otp_hash,
            email_verification_otp_expires=(
                 datetime.utcnow() + timedelta(minutes=5)
            ),
            email_verification_attempts = 0
        )

        db.session.add(customer)
        db.session.commit()

        email_sent = send_verification_email(
             customer,
             otp
        )

        if not email_sent:
             db.session.delete(customer)
             db.session.commit()

             flash(
                  "Unable to send verification email. Please try again.",
                  "error"
             )
             return redirect(
                  url_for("auth.register")
             )

        flash(
             "Account created! Please check your email to verify your account.",
             "success"
        )

       
        return redirect(url_for("auth.verify_otp",email=email))

    return render_template("auth/register.html")



@auth.route("/verify-otp",methods = ["GET","POST"])
@limiter.limit("10 per hour")
def verify_otp():
     if request.method == "POST":
          email = request.form.get(
               "email",""
          ).strip().lower()

          otp = request.form.get("otp","").strip()

          if not valid_email(email):
               flash("Invalid email address.","error")
               return redirect(url_for("auth.verify_otp"))

          if not otp.isdigit() or len(otp) != 6:
               flash("Please enter a valid 6-digit OTP.","error")
               return redirect(url_for("auth.verify_otp",email=email))

          customer = Customer.query.filter_by(email=email).first()

          if not customer:
               flash("Invalid verification request.","error")
               return redirect(url_for("auth.verify_otp"))
          if customer.email_verified:
            flash(
                "Your email is already verified.",
                "success"
            )
            return redirect(
                url_for("auth.login")
            )
          if(not customer.email_verification_otp_expires or customer.email_verification_otp_expires < datetime.utcnow()):
               flash("This OTP has expired. Please request a new one.","error")
               return redirect(url_for("auth.verify_otp",email=email))
          if customer.email_verification_attempts >= 5:
               flash("Too many incorrect attempts. Please request a new OTP.","error")
               return redirect(url_for("auth.verify_otp",email=email))
          if not check_password_hash(customer.email_verification_otp_hash,otp):
               customer.email_verification_attempts += 1
               db.session.commit()
               flash("Incorrect OTP.","error")
               return redirect(url_for("auth.verify_otp",email=email))


          customer.email_verified = True
          customer.email_verification_otp_hash = None
          customer.email_verification_otp_expires = None
          customer.email_verification_attempts = 0

          db.session.commit()

          flash("Email verified successfully! You can now log in.", "success")
          return redirect(url_for("auth.login"))

     email = request.args.get("email","").strip().lower()

     return render_template("auth/verify_otp.html",email=email)


@auth.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def forgot_password():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        if not valid_email(email):
            flash(
                "Please enter a valid email address.",
                "error"
            )
            return redirect(
                url_for("auth.forgot_password")
            )

        customer = Customer.query.filter_by(
            email=email
        ).first()

        # IMPORTANT:
        # Do not reveal whether the email exists.
        if not customer:
            flash(
                "If an account exists with this email, "
                "a verification code has been sent.",
                "success"
            )

            return redirect(
                url_for("auth.forgot_password")
            )

        # Cooldown: no new code within 60s of the last one. Stops email spam and
        # stops an attacker from endlessly resetting the wrong-attempt counter.
        if (
            customer.password_reset_otp_expires
            and customer.password_reset_otp_expires > datetime.utcnow() + timedelta(minutes=9)
        ):
            flash(
                "If an account exists with this email, "
                "a verification code has been sent.",
                "success"
            )
            return redirect(url_for("auth.reset_password_otp", email=email))

        otp = generate_otp()

        otp_hash = generate_password_hash(otp)

        customer.password_reset_otp_hash = otp_hash

        customer.password_reset_otp_expires = (
            datetime.utcnow() + timedelta(minutes=10)
        )

        customer.password_reset_attempts = 0

        db.session.commit()

        email_sent = send_password_reset_email(
            customer,
            otp
        )

        if not email_sent:

            # Clear the OTP because it was not delivered.
            customer.password_reset_otp_hash = None
            customer.password_reset_otp_expires = None
            customer.password_reset_attempts = 0

            db.session.commit()

            flash(
                "Unable to send the verification email. "
                "Please try again.",
                "error"
            )

            return redirect(
                url_for("auth.forgot_password")
            )

        flash(
            "If an account exists with this email, "
            "a verification code has been sent.",
            "success"
        )

        return redirect(
            url_for(
                "auth.reset_password_otp",
                email=email
            )
        )

    return render_template(
        "auth/forgot_password.html"
    )

@auth.route("/reset-password-otp", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def reset_password_otp():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        otp = request.form.get(
            "otp",
            ""
        ).strip()

        if not valid_email(email):
            flash(
                "Invalid verification request.",
                "error"
            )
            return redirect(
                url_for("auth.forgot_password")
            )

        if not otp.isdigit() or len(otp) != 6:
            flash(
                "Please enter a valid 6-digit OTP.",
                "error"
            )
            return redirect(
                url_for(
                    "auth.reset_password_otp",
                    email=email
                )
            )

        customer = Customer.query.filter_by(
            email=email
        ).first()

        if not customer:
            flash(
                "Invalid verification request.",
                "error"
            )
            return redirect(
                url_for("auth.forgot_password")
            )


        if (
            not customer.password_reset_otp_expires
            or
            customer.password_reset_otp_expires < datetime.utcnow()
        ):
            flash(
                "This OTP has expired. Please request a new one.",
                "error"
            )
            return redirect(
                url_for(
                    "auth.reset_password_otp",
                    email=email
                )
            )

  
        if customer.password_reset_attempts >= 5:
            flash(
                "Too many incorrect attempts. Please request a new OTP.",
                "error"
            )
            return redirect(
                url_for(
                    "auth.reset_password_otp",
                    email=email
                )
            )

        if not check_password_hash(
            customer.password_reset_otp_hash,
            otp
        ):

            customer.password_reset_attempts += 1

            db.session.commit()

            flash(
                "Incorrect OTP.",
                "error"
            )

            return redirect(
                url_for(
                    "auth.reset_password_otp",
                    email=email
                )
            )

        customer.password_reset_otp_hash = None
        customer.password_reset_otp_expires = None
        customer.password_reset_attempts = 0

        db.session.commit()

        session["password_reset_verified"] = True
        session["password_reset_email"] = email

        return redirect(
            url_for(
                "auth.reset_password"
            )
        )

    email = request.args.get(
        "email",
        ""
    ).strip().lower()

    return render_template(
        "auth/reset_password_otp.html",
        email=email
    )


@auth.route("/reset-password", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def reset_password():

    if not session.get("password_reset_verified"):
        flash(
            "Please verify your email first.",
            "error"
        )
        return redirect(url_for("auth.forgot_password"))

    email = session.get("password_reset_email")

    if not email:
        session.pop("password_reset_verified", None)
        return redirect(url_for("auth.forgot_password"))

    customer = Customer.query.filter_by(
        email=email
    ).first()

    if not customer or not customer.is_active:
        session.pop("password_reset_verified", None)
        session.pop("password_reset_email", None)

        flash(
            "Invalid password reset request.",
            "error"
        )
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not valid_password(password):
            flash(
                "Password must be at least 8 characters and contain "
                "uppercase, lowercase and a number.",
                "error"
            )
            return redirect(url_for("auth.reset_password"))

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "error"
            )
            return redirect(url_for("auth.reset_password"))

        customer.password = generate_password_hash(password)

        db.session.commit()

        # Destroy password-reset authorization
        session.pop("password_reset_verified", None)
        session.pop("password_reset_email", None)

        flash(
            "Password reset successfully! You can now log in.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template(
        "auth/reset_password.html"
    )


@auth.route("/user_login",methods=["GET","POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")

        customer = Customer.query.filter_by(email=email).first()

        if not customer or not customer.is_active:
            flash("Invalid email or password.", "error")
            return render_template("auth/user_login.html")

        if not check_password_hash(customer.password, password):
            flash("Invalid email or password.", "error")
            return render_template("auth/user_login.html")

        if not customer.email_verified:
            flash(
                "Please verify your email before logging in.",
                "error"
            )
            return render_template("auth/user_login.html")

        login_user(customer, remember=False)

        flash("Logged in successfully!", "success")

        return redirect(url_for("home"))

    return render_template("auth/user_login.html")

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully!", "success")

    return redirect(url_for("home"))

