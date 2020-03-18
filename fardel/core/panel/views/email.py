from flask import (request, render_template, redirect, url_for,
                   jsonify, abort, current_app, flash)
from flask_login import current_user, login_required
from flask_babel import gettext, pgettext

from fardel.core import email as email_pkg

from .. import mod, staff_required, permission_required


@mod.route('/communication/email/send/', methods=["GET", "POST"])
@permission_required("can_send_email")
@staff_required
@login_required
def email_send():
    if request.method == "POST":
        sender = request.form.get("sender")
        recievers = request.form.getlist("recievers")
        title = request.form.get("title")
        content = request.form.get("content")

        if not sanity_check_email_addresses(sender, *recievers):
            flash("Emails are not correct")
            return redirect(url_for("panel.email_send"))

        message = {
            "subject": title,
            "text": content,
            "html": content,
            "from": sender,
            "to": recievers,
        }
        email_pkg.send_email(message)

        flash("Messages are sent")
        return redirect(url_for("panel.email_send"))
    return render_template("communication/send_email.html")


def sanity_check_email_addresses(*emails):
    print(emails)
    for email in emails:
        if not "@" in email:
            return False
    return True
