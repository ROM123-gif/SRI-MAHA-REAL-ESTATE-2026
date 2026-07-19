from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "realestate123"

# ---------------- UPLOAD FOLDER ---------------- #

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- DATABASE ---------------- #

# ---------------- DATABASE ---------------- #

db = mysql.connector.connect(
    host="mysql-2aa2f818-romulasnirmal661-5570.e.aivencloud.com",
    user="avnadmin",
    password=os.environ.get("DB_PASSWORD"),
    database="defaultdb",
    port=14708
)

cursor = db.cursor(dictionary=True)

# ---------------- HOME ---------------- #

@app.route("/")
def home():

    cursor.execute("""
        SELECT * FROM properties
        ORDER BY id DESC
    """)

    properties = cursor.fetchall()

    return render_template(
        "index.html",
        properties=properties
    )

# ---------------- ABOUT ---------------- #

@app.route("/about")
def about():
    return render_template("about.html")

# ---------------- SERVICES ---------------- #

@app.route("/services")
def services():
    return render_template("services.html")

# ---------------- CONTACT ---------------- #

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]

        cursor.execute("""
            INSERT INTO enquiries
            (name, email, phone, message)
            VALUES (%s, %s, %s, %s)
        """, (name, email, phone, message))

        db.commit()

        return render_template(
            "contact.html",
            success="Your enquiry has been sent successfully!"
        )

    return render_template("contact.html")

# ---------------- PROPERTIES ---------------- #

@app.route("/properties")
def properties():

    search = request.args.get("search")

    if search:

        cursor.execute("""
            SELECT * FROM properties
            WHERE
            title LIKE %s
            OR location LIKE %s
            ORDER BY id DESC
        """, (
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cursor.execute("""
            SELECT * FROM properties
            ORDER BY id DESC
        """)

    properties = cursor.fetchall()

    return render_template(
        "properties.html",
        properties=properties
    )

# ---------------- PROPERTY DETAILS ---------------- #

@app.route("/property/<int:id>")
def property_details(id):

    cursor.execute(
        "SELECT * FROM properties WHERE id=%s",
        (id,)
    )

    property = cursor.fetchone()

    if property is None:
        return "Property Not Found"

    return render_template(
        "property_details.html",
        property=property
    )

# ---------------- LOGIN ---------------- #

@app.route("/login")
def login():

    if "admin" in session:
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():

    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":

        session["admin"] = username

        return redirect(url_for("dashboard"))

    return render_template(
        "login.html",
        error="Invalid Username or Password"
    )

# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect(url_for("login"))

    # Properties
    cursor.execute("SELECT * FROM properties ORDER BY id DESC")
    properties = cursor.fetchall()

    # Total Properties
    cursor.execute("SELECT COUNT(*) AS total_properties FROM properties")
    total_properties = cursor.fetchone()["total_properties"]

    # Total Enquiries
    cursor.execute("SELECT COUNT(*) AS total_enquiries FROM enquiries")
    total_enquiries = cursor.fetchone()["total_enquiries"]

    return render_template(
        "dashboard.html",
        properties=properties,
        total_properties=total_properties,
        total_enquiries=total_enquiries
    )
    # ---------------- VIEW ENQUIRIES ---------------- #

# ---------------- VIEW ENQUIRIES ---------------- #

@app.route("/enquiries")
def enquiries():

    if "admin" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search")

    if search:

        cursor.execute("""
            SELECT * FROM enquiries
            WHERE
            name LIKE %s
            OR email LIKE %s
            OR phone LIKE %s
            ORDER BY id DESC
        """, (
            "%" + search + "%",
            "%" + search + "%",
            "%" + search + "%"
        ))

    else:

        cursor.execute("""
            SELECT * FROM enquiries
            ORDER BY id DESC
        """)

    enquiries = cursor.fetchall()

    return render_template(
        "enquiries.html",
        enquiries=enquiries
    )
    # ---------------- DELETE ENQUIRY ---------------- #

@app.route("/delete-enquiry/<int:id>")
def delete_enquiry(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    cursor.execute(
        "DELETE FROM enquiries WHERE id=%s",
        (id,)
    )

    db.commit()

    return redirect(url_for("enquiries"))
    # ---------------- ADD PROPERTY ---------------- #

@app.route("/add-property")
def add_property():

    if "admin" not in session:
        return redirect(url_for("login"))

    return render_template("add_property.html")


@app.route("/save-property", methods=["POST"])
def save_property():

    if "admin" not in session:
        return redirect(url_for("login"))

    title = request.form["title"]
    location = request.form["location"]
    price = request.form["price"]
    description = request.form["description"]

    image = request.files["image"]

    filename = ""

    if image and image.filename != "":
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    cursor.execute("""
        INSERT INTO properties
        (title, location, price, image, description)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        title,
        location,
        price,
        filename,
        description
    ))

    db.commit()

    return redirect(url_for("dashboard"))


# ---------------- EDIT PROPERTY ---------------- #

@app.route("/edit-property/<int:id>")
def edit_property(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    cursor.execute(
        "SELECT * FROM properties WHERE id=%s",
        (id,)
    )

    property = cursor.fetchone()

    if property is None:
        return "Property Not Found"

    return render_template(
        "edit_property.html",
        property=property
    )


@app.route("/update-property/<int:id>", methods=["POST"])
def update_property(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    cursor.execute(
        "SELECT * FROM properties WHERE id=%s",
        (id,)
    )

    property = cursor.fetchone()

    if property is None:
        return "Property Not Found"

    title = request.form["title"]
    location = request.form["location"]
    price = request.form["price"]
    description = request.form["description"]

    filename = property["image"]

    image = request.files["image"]

    if image and image.filename != "":

        # Delete old image
        if filename:

            old_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            if os.path.exists(old_path):
                os.remove(old_path)

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

    cursor.execute("""
        UPDATE properties
        SET
        title=%s,
        location=%s,
        price=%s,
        image=%s,
        description=%s
        WHERE id=%s
    """, (
        title,
        location,
        price,
        filename,
        description,
        id
    ))

    db.commit()

    return redirect(url_for("dashboard"))


# ---------------- DELETE PROPERTY ---------------- #

@app.route("/delete-property/<int:id>")
def delete_property(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    cursor.execute(
        "SELECT * FROM properties WHERE id=%s",
        (id,)
    )

    property = cursor.fetchone()

    if property:

        if property["image"]:

            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                property["image"]
            )

            if os.path.exists(image_path):
                os.remove(image_path)

        cursor.execute(
            "DELETE FROM properties WHERE id=%s",
            (id,)
        )

        db.commit()

    return redirect(url_for("dashboard"))


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------- START APP ---------------- #

if __name__ == "__main__":

    app.run(
        debug=True
    )
