from smtplib import SMTPRecipientsRefused

from flask import Blueprint, request, render_template, flash, redirect, url_for
from itsdangerous import BadSignature
from wtforms import ValidationError

from forms import RegisterForm, UnsubscribeForm, PreferencesForm, UpdateForm
import actions
import constants
import auth

api = Blueprint("api", __name__)


def homepage():
    form = RegisterForm()
    if request.method == "POST":

        print(form.errors)
        try:
            _, duplicate_user = actions.register_new_user(form.email.data, form.postcode.data)
            if duplicate_user:
                flash(f" We seem to have you registered already, but we've resent your confirmation email!")
            else:
                flash(f"We've sent a confirmation email to {form.email.data}, please check your inbox!")
            return redirect(url_for("api.registered"))
        except SMTPRecipientsRefused:
            if not form.email.data:
                flash(f"Did you forget to enter an email?")
            else:
                flash(
                    f"We couldn't send an email to {form.email.data}, please check and try again!", category="warning"
                )
        except IndexError:
            if not form.postcode.data:
                flash(f"Did you forget to enter a location?")
            else:
                flash(f" We couldn't find a location for {form.postcode.data}, please check and try again!")
        except:
            flash(
                "As of September 2021 Weather Window is no longer accepting new users. This is due to security changes from Google"
                " which make it difficult for us to maintain the service 😭. Thank you for your interest 🙏 "
            )

    return render_template("register.html", title="Weather Window", form=form, GOOGLE_API_KEY=constants.GOOGLE_API_KEY)


@api.route("/", methods=["GET", "POST"])
def register():
    return homepage()


@api.route("/registered", methods=["GET", "POST"])
def registered():
    return homepage()


@api.route("/preferences/<token>", methods=["GET", "POST"])
def preferences(token, header="Update your preferences", subheader="Customize your weather window"):
    email = auth.decode_token_to_email(token)
    form = PreferencesForm()

    if request.method == "POST":
        try:
            form.validate()
            actions.update_preferences_for_user_from_form(email, form=form)
            flash(
                f"We've updated your preferences, thanks. You'll see this reflected in the next "
                f"weather window we send you!"
            )
            return redirect(url_for("api.index"))
        except ValidationError as error:
            flash(error, category="error")

    form.initialize_from_db(actions.add_or_return_user_preferences(email))
    return render_template(
        "confirm.html", title="Weather Window: Preferences", header=header, subheader=subheader, form=form
    )


@api.route("/unsubscribe", methods=["GET", "POST"])
def unsubscribe_page():
    form = UnsubscribeForm()
    if request.method == "POST":
        try:
            email = form.email.data
            actions.send_unsubscribe_email(email)
            flash(f"Unsubscribe email sent to {email}")
        except ValueError:
            flash(f"We couldn't find that user, have you already unsubscribed?")

    return render_template("unsubscribe.html", form=form)


@api.route("/changepreferences", methods=["GET", "POST"])
def preferences_page():
    form = UpdateForm()
    if request.method == "POST":
        try:
            email = form.email.data
            try:
                actions.send_update_preferences_email(email)
                flash(f"We've sent a link to edit your preferences to {email}")
            except:
                flash("We're not able to update preferences due to Google blocking our outgoing emails 😭")

        except ValueError:
            flash(f"We couldn't find that user, have you already unsubscribed?")

    return render_template("change_preferences.html", form=form)


@api.route("/")
def index():
    return render_template("base.html")


@api.route("/ping")
def ping():
    return "pong"


@api.route("/confirm/<token>", methods=["GET", "POST"])
def confirm_email(token):
    email = auth.decode_token_to_email(token)
    if email is None:
        flash("This confirmation link is invalid or has expired", "danger")
        redirect(url_for("api.index"))
    else:
        print(f"Email confirmed for user {email}")
        user = actions.get_user(email)
        if user is None:
            flash("Uho, you were already unsubscribed! Please subscribe again")
        actions.set_email_verified(user_row=user)
        # TODO: we can do this async, move it to a cron job

        try:
            actions.send_tomorrow_window_to_user(user=user)
            flash("Email confirmed, thanks! Check your calendar, you should have an invite for tomorrow!", "success")
        except Exception as e:
            print(f"New user invite failed - {e}")
            flash("Email confirmed, thanks! We will send you a calendar invite for tomorrow shortly!", "success")

    return redirect(
        url_for(
            "api.preferences",
            token=token,
            header="You're all set!",
            subheader="We've confirmed your email and sent you an invite for tomorrow",
        )
    )


@api.route("/unsubscribe/<token>", methods=["GET", "POST"])
def unsubscribe(token):
    try:
        email = auth.decode_token_to_email(token)
        if email is None:
            flash("This unsubscribe link is invalid! Please try again", "danger")
        else:
            print(f"Unsubscribe confirmed for user {email}")
            actions.delete_user(email)

            flash("You've been unsubscribed. Starting tomorrow, you won't receive new invites.", "success")

    except BadSignature:
        print("Bad signature error")

    return redirect(url_for("api.index"))


@api.route("/google79a68bb5bf16f86a.html")
def google_verification():
    return render_template("google.html")
