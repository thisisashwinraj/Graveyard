import base64
import re
import requests
import time
import streamlit as st
import streamlit_authenticator as stauth
from PIL import Image

import firebase_admin
from firebase_admin import auth, credentials

from configurations.api_authtoken import AuthTokens


if "user_authentication_status" not in st.session_state:
    st.session_state.user_authentication_status = None

if "authenticated_user_email_id" not in st.session_state:
    st.session_state.authenticated_user_email_id = None

if "authenticated_user_username" not in st.session_state:
    st.session_state.authenticated_user_username = None


def _valid_name(fullname):
    if not re.match(r"^[A-Z][a-z]+( [A-Z][a-z]+)*$", fullname):
        return False

    return True  


def _valid_username(username):
    if len(username) < 4:
        return False, "MINIMUM_LENGTH_UID"
    if len(username) > 25:
        return False, "MAXIMUM_LENGTH_UID"

    allowed_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_."
    )
    if not all(char in allowed_chars for char in username):
        return False, "INVALID_CHARACTERS"

    if not username[0].isalpha():
        return False, "START_WITH_LETTERS"

    return True, "USERNAME_VALID"


def _valid_email_address(email):
    email_regex = r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None


def signup_form():
    if st.session_state.user_authentication_status is not True:
        with st.form("register_new_user_form"):
            st.markdown(
                '<H3 id="anchor-create-user">Register Now to Create an Account</H3>',
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p align='justify' style='color: #e2e2e2;'>Level up your recipe game! Get personalized recipe recommendations, create custom meal plans and more. Signup for your free RecipeML account today! Already have a account? LogIn now to get started</p>",
                unsafe_allow_html=True,
            )

            signup_form_section_1, signup_form_section_2 = st.columns(2)

            with signup_form_section_1:
                name = st.text_input(
                    "Enter your Full Name:",
                )
                email = st.text_input(
                    "Enter your E-Mail Id:",
                )

            with signup_form_section_2:
                username = st.text_input(
                    "Enter your Username:",
                    placeholder="Allowed characters: A-Z, 0-9, . & _",
                )
                phone_number = st.text_input(
                    "Enter Phone Number:",
                    placeholder="Include your Country Code (eg: +91)",
                )

            password = st.text_input(
                "Enter your Password:",
                type="password",
            )

            accept_terms_and_conditions = st.checkbox(
                "By creating an account, you confirm your acceptance to our Terms of Use and the Privacy Policy"
            )
            button_section_1, button_section_2, button_section_3 = st.columns(3)

            with button_section_1:
                submitted = st.form_submit_button(
                    "Register Now", use_container_width=True
                )

            if submitted:
                try:
                    if not name:
                        st.toast("Please enter your full name")
                    elif not _valid_name(name):
                        st.toast("Not quite! Double-check your full name.")

                    elif not _valid_username(username)[0]:
                        validation_error_message = _valid_username(username)[1]

                        if validation_error_message == "MINIMUM_LENGTH_UID":
                            st.toast("Username too short! Needs 4+ letters.")

                        elif validation_error_message == "MAXIMUM_LENGTH_UID":
                            st.toast("Username too long! Max 25 letters.")

                        elif validation_error_message == "INVALID_CHARACTERS":
                            st.toast("Username contains invalid charecters!")
                            time.sleep(1.5)
                            st.toast("Try again with valid chars (a-z, 0-9, ._)")

                        elif validation_error_message == "START_WITH_LETTERS":
                            st.toast("Start your username with a letter.")

                        else:
                            st.toast("Invalid Username! Try again.")

                    elif not _valid_email_address(email):
                        st.toast("Invalid email format. Please try again.")

                    elif len(password) < 8:
                        st.toast("Password too short! Needs 8+ characters.")

                    elif not accept_terms_and_conditions:
                        st.toast("Please accept our terms of use")

                    else:
                        firebase_admin.auth.create_user(
                            uid=username.lower(),
                            display_name=name,
                            email=email,
                            phone_number=phone_number,
                            password=password,
                        )
                        st.toast("Welcome to RecipeML!")

                        alert_successful_account_creation = st.success(
                            "Your Account has been created successfully"
                        )
                        time.sleep(2)

                        st.toast("Please login to access your account.")
                        time.sleep(3)
                        alert_successful_account_creation.empty()

                except Exception as error:
                    if "Invalid phone number" in str(error):
                        st.toast("Invalid phone number format.")

                        time.sleep(1.5)
                        st.toast("Please check country code and + prefix.")

                    elif "PHONE_NUMBER_EXISTS" in str(error):
                        st.toast("User with phone number already exists")

                    elif "DUPLICATE_LOCAL_ID" in str(error):
                        st.toast("The username is already taken")

                    elif "EMAIL_EXISTS" in str(error):
                        st.toast("User with provided email already exists")

                    else:
                        alert_failed_account_creation = st.warning(
                            "Oops! We could not create your account. Please check your connectivity and try again."
                        )
                        time.sleep(7)
                        alert_failed_account_creation.empty()


def fetch_user_full_name_by_username(username):
    user = firebase_admin.auth.get_user(username)
    return user.display_name


def login_form():
    if st.session_state.user_authentication_status is not True:
        auth_token = AuthTokens()
        with st.sidebar.form("login_existing_user_form"):
            email = st.text_input(
                "Username / Email Id:", placeholder="Username or email address"
            )
            password = st.text_input(
                "Enter your Password:", type="password", placeholder="Password"
            )

            submitted_login = st.form_submit_button(
                "LogIn to Smartspace", use_container_width=True
            )
            st.markdown(
                "&nbsp;New to Smartspace? <A href='#register-now-to-create-an-account' style='color: #64ABD8;'>Create account</A>",
                unsafe_allow_html=True,
            )

            if submitted_login:
                try:
                    api_key = auth_token.firebase_api_key
                    base_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

                    if "@" not in email:
                        username = email
                        user = firebase_admin.auth.get_user(username)
                        email = user.email

                    data = {"email": email, "password": password}
                    response = requests.post(
                        base_url.format(api_key=api_key), json=data
                    )

                    if response.status_code == 200:
                        data = response.json()

                        user_display_name = data["displayName"]
                        user_email_id = email
                        user_username = firebase_admin.auth.get_user_by_email(email).uid

                        user_phone_number = firebase_admin.auth.get_user_by_email(
                            email
                        ).phone_number

                        st.session_state.user_authentication_status = True
                        st.session_state.authenticated_user_email_id = user_email_id
                        st.session_state.authenticated_user_username = user_username

                        st.rerun()

                    else:
                        data = response.json()
                        login_error_message = str(data["error"]["message"])

                        if login_error_message == "INVALID_PASSWORD":
                            authentication_failed_alert = st.sidebar.warning(
                                "&nbsp; Invalid password. Try again.", icon="⚠️"
                            )
                        elif login_error_message == "EMAIL_NOT_FOUND":
                            authentication_failed_alert = st.sidebar.warning(
                                "&nbsp; User with this mail doesn't exist.", icon="⚠️"
                            )
                        else:
                            authentication_failed_alert = st.sidebar.warning(
                                "&nbsp; Unable to login. Try again later.", icon="⚠️"
                            )

                        time.sleep(2)
                        authentication_failed_alert.empty()

                        st.session_state.user_authentication_status = False
                        st.session_state.authenticated_user_email_id = None
                        st.session_state.authenticated_user_username = None

                except Exception as err:
                    authentication_failed_alert = st.sidebar.warning(
                        "&nbsp; Username not found. Try again!", icon="⚠️"
                    )
                    print(err)

                    time.sleep(2)
                    authentication_failed_alert.empty()

                    st.session_state.user_authentication_status = False
                    st.session_state.authenticated_user_email_id = None
                    st.session_state.authenticated_user_username = None

    return (
        st.session_state.user_authentication_status,
        st.session_state.authenticated_user_email_id,
        st.session_state.authenticated_user_username,
    )


def logout_button():
    if st.sidebar.button("Logout from RecipeML", use_container_width=True):
        st.session_state.user_authentication_status = None
        st.session_state.authenticated_user_email_id = None
        st.session_state.authenticated_user_username = None
        st.rerun()


def reset_password_form():
    with st.sidebar.expander("Forgot password"):
        auth_token = AuthTokens()
        api_key = auth_token.firebase_api_key
        base_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"

        email = st.text_input(
            "Enter your registered email id", placeholder="Registered email address"
        )

        if st.button("Reset Password", use_container_width=True):
            data = {"requestType": "PASSWORD_RESET", "email": email}
            response = requests.post(base_url.format(api_key=api_key), json=data)

            if response.status_code == 200:
                alert_password_reset_mail_sent = st.success(
                    "A password reset mail is on its way!"
                )
                st.toast("Success! Password reset email sent.")

                time.sleep(2)
                st.toast("Check your mailbox for next steps.")

                time.sleep(3)
                alert_password_reset_mail_sent.empty()

            else:
                alert_password_reset_mail_failed = st.error(
                    "Failed to send password reset mail"
                )
                st.toast("We're having trouble sending the email.")

                time.sleep(2)
                st.toast("Double-check your mail id and try again")

                time.sleep(3)
                alert_password_reset_mail_failed.empty()


try:
    firebase_credentials = credentials.Certificate(
        "configurations/recipeml_firebase_secrets.json"
    )
    firebase_admin.initialize_app(firebase_credentials)

except Exception as err: pass