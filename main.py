from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel
from dotenv import load_dotenv
import smtplib
import sqlite3
import re
import random
import os

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

app = FastAPI()
reset_otps = {}
def send_otp_email(receiver_email, otp):

    subject = "Your OTP Verification Code"

    body = f"""
Your OTP is: {otp}

Please use this OTP to complete the verification.
"""

    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP("smtp.gmail.com", 587) as server:

        server.starttls()

        server.login(
            EMAIL_ADDRESS,
            EMAIL_PASSWORD
        )

        server.sendmail(
            EMAIL_ADDRESS,
            receiver_email,
            message
        )

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def show_register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )




class UserRegistration(BaseModel):
    full_name: str
    email: str
    phone: str
    dob: str
    password: str


@app.post("/register")
def register_user(user: UserRegistration):

    password = user.password

    if len(password) < 10:
        return {
            "message": "Password must contain at least 10 characters!"
        }

    if not re.search(r"[A-Za-z]", password):
        return {
            "message": "Password must contain at least one alphabet!"
        }

    if not re.search(r"[0-9]", password):
        return {
            "message": "Password must contain at least one number!"
        }

    if not re.search(r"[^A-Za-z0-9]", password):
        return {
            "message": "Password must contain at least one special character!"
        }

    otp = str(random.randint(100000, 999999))
    send_otp_email(user.email, otp)

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (
                full_name,
                email,
                phone,
                dob,
                password,
                otp
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user.full_name,
            user.email,
            user.phone,
            user.dob,
            user.password,
            otp
        ))

        connection.commit()
        send_otp_email(user.email, otp)

        return {
    "success": True,
    "message": "Registration successful! OTP has been sent to your email."
}
    except sqlite3.IntegrityError:
        return {
            "message": "This email is already registered!"
        }

    finally:
        connection.close()


class EmailVerification(BaseModel):
    email: str
    otp: str


@app.post("/verify-email")
def verify_email(data: EmailVerification):

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT otp FROM users WHERE email = ?",
        (data.email,)
    )

    user = cursor.fetchone()

    if user is None:
        connection.close()

        return {
            "message": "User not found!"
        }

    stored_otp = user[0]

    if stored_otp != data.otp:
        connection.close()

        return {
            "message": "Invalid OTP!"
        }

    cursor.execute(
        "UPDATE users SET is_verified = 1 WHERE email = ?",
        (data.email,)
    )

    connection.commit()
    connection.close()

    return {
        "message": "Email verified successfully!"
    }
@app.get("/verify", response_class=HTMLResponse)
def show_verify_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="verify.html"
    )



class UserLogin(BaseModel):
    email: str
    password: str


@app.post("/login")
def login_user(user: UserLogin):

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT email, password, is_verified
        FROM users
        WHERE email = ?
        """,
        (user.email,)
    )

    database_user = cursor.fetchone()

    connection.close()

    if database_user is None:
        return {
            "message": "User not found!"
        }

    stored_email = database_user[0]
    stored_password = database_user[1]
    is_verified = database_user[2]

    if stored_password != user.password:
        return {
            "message": "Incorrect password!"
        }

    if is_verified == 0:
        return {
            "message": "Email is not verified. Please verify your email first.",
            "redirect": "/verify"
        }

    return {
        "message": "Login successful!",
        "redirect": "/dashboard"
    }



@app.get("/profile")
def get_profile(email: str):

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT full_name, email, phone, dob
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    connection.close()

    if user is None:
        return {
            "message": "User not found!"
        }

    return {
        "full_name": user[0],
        "email": user[1],
        "phone": user[2],
        "dob": user[3]
    }


@app.get("/dashboard", response_class=HTMLResponse)
def show_dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )


@app.get("/login", response_class=HTMLResponse)
def show_login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


class ProfileUpdate(BaseModel):
    email: str
    full_name: str
    phone: str
    dob: str


@app.put("/update-profile")
def update_profile(data: ProfileUpdate):

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET full_name = ?, phone = ?, dob = ?
        WHERE email = ?
    """, (
        data.full_name,
        data.phone,
        data.dob,
        data.email
    ))

    connection.commit()

    updated_rows = cursor.rowcount

    connection.close()

    if updated_rows == 0:
        return {
            "success": False,
            "message": "User not found!"
        }

    return {
        "success": True,
        "message": "Profile updated successfully!"
    }


@app.post("/upload-profile-picture")
async def upload_profile_picture(
    email: str = Form(...),
    file: UploadFile = File(...)
):

    file_extension = file.filename.split(".")[-1]

    file_name = (
        email.replace("@", "_").replace(".", "_")
        + "."
        + file_extension
    )

    file_path = os.path.join(
        "static",
        "uploads",
        file_name
    )

    file_content = await file.read()

    with open(file_path, "wb") as image_file:
        image_file.write(file_content)

    return {
        "success": True,
        "message": "Profile picture uploaded successfully!",
        "image_url": "/static/uploads/" + file_name
    }



@app.delete("/delete-profile-picture")
def delete_profile_picture(email: str):

    upload_folder = os.path.join("static", "uploads")

    possible_extensions = ["jpg", "jpeg", "png", "webp"]

    deleted = False

    for extension in possible_extensions:

        file_name = (
            email.replace("@", "_").replace(".", "_")
            + "."
            + extension
        )

        file_path = os.path.join(
            upload_folder,
            file_name
        )

        if os.path.exists(file_path):
            os.remove(file_path)
            deleted = True

    if deleted:
        return {
            "success": True,
            "message": "Profile picture deleted successfully!"
        }

    return {
        "success": False,
        "message": "Profile picture not found!"
    }


class PasswordChange(BaseModel):
    email: str
    current_password: str
    new_password: str


@app.put("/change-password")
def change_password(data: PasswordChange):

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE email = ?",
        (data.email,)
    )

    user = cursor.fetchone()

    if user is None:
        connection.close()

        return {
            "success": False,
            "message": "User not found!"
        }

    stored_password = user[0]

    if stored_password != data.current_password:
        connection.close()

        return {
            "success": False,
            "message": "Current password is incorrect!"
        }

    new_password = data.new_password

    if len(new_password) < 10:
        connection.close()

        return {
            "success": False,
            "message": "Password must contain at least 10 characters!"
        }

    if not re.search(r"[A-Za-z]", new_password):
        connection.close()

        return {
            "success": False,
            "message": "Password must contain at least one alphabet!"
        }

    if not re.search(r"[0-9]", new_password):
        connection.close()

        return {
            "success": False,
            "message": "Password must contain at least one number!"
        }

    if not re.search(r"[^A-Za-z0-9]", new_password):
        connection.close()

        return {
            "success": False,
            "message": "Password must contain at least one special character!"
        }

    cursor.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (new_password, data.email)
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "message": "Password changed successfully!"
    }
@app.get("/change-password", response_class=HTMLResponse)
def show_change_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="change_password.html"
    )

class ForgotPassword(BaseModel):
    email: str

@app.get("/forgot-password", response_class=HTMLResponse)
def show_forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="forgot_password.html"
    )
@app.post("/forgot-password")
def forgot_password(data: ForgotPassword):

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT email FROM users WHERE email = ?",
        (data.email,)
    )

    user = cursor.fetchone()

    connection.close()

    if user is None:
        return {
            "success": False,
            "message": "Email not found!"
        }

    otp = random.randint(100000, 999999)

    reset_otps[data.email] = otp
    send_otp_email(data.email, otp)

    return {
        "success": True,
        "message": "OTP generated successfully!"
    }

class ResetPassword(BaseModel):
    email: str
    otp: int
    new_password: str


@app.put("/reset-password")
def reset_password(data: ResetPassword):

    if data.email not in reset_otps:
        return {
            "success": False,
            "message": "Please request an OTP first!"
        }

    stored_otp = reset_otps[data.email]

    if stored_otp != data.otp:
        return {
            "success": False,
            "message": "Invalid OTP!"
        }

    new_password = data.new_password

    if len(new_password) < 10:
        return {
            "success": False,
            "message": "Password must contain at least 10 characters!"
        }

    if not re.search(r"[A-Za-z]", new_password):
        return {
            "success": False,
            "message": "Password must contain at least one alphabet!"
        }

    if not re.search(r"[0-9]", new_password):
        return {
            "success": False,
            "message": "Password must contain at least one number!"
        }

    if not re.search(r"[^A-Za-z0-9]", new_password):
        return {
            "success": False,
            "message": "Password must contain at least one special character!"
        }

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (new_password, data.email)
    )

    connection.commit()
    connection.close()

    del reset_otps[data.email]

    return {
        "success": True,
        "message": "Password reset successfully!"
    }

@app.get("/reset-password", response_class=HTMLResponse)
def show_reset_password_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="reset_password.html"
    )

@app.get("/logout")
def logout():
    return RedirectResponse(url="/login")

@app.delete("/delete-user/{email}")
def delete_user(email: str):

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM users WHERE email = ?",
        (email,)
    )

    connection.commit()
    connection.close()

    return {
        "message": "User deleted successfully!"
    }