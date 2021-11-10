from flask import Flask
from flask import render_template
from flask import redirect, url_for
from files4libs import cipac

app = Flask(__name__)

app.config['DEBUG']


catalog = cipac.Catalog("http://localhost/bnjmsculyfof")
card = cipac.Card("http://localhost/bnjmsculyfof", 1, 1)

@app.context_processor
def provide_catalog():
    catalog = cipac.Catalog("http://localhost/bnjmsculyfof")
    return {'catalog': catalog}

@app.context_processor
def provide_card():
    card = cipac.Card("http://localhost/bnjmsculyfof",1,1)
    return {'card': card}
    
@app.route("/")
def home():
    return redirect(url_for('show_card', card_id="bnjmsculyfof"))


@app.route("/about/")
def about():
    # return "{} Catalog has {} cards in {} drawers".format(catalog.id,catalog.q_cards,catalog.q_drawers)
    return render_template("about.html", catalog=catalog)


@app.route("/cards/<string:card_id>/", methods=["GET"])
def show_card(card_id):
    if len(card_id) == 12:
        i = 1
        j = 1
    elif len(card_id) == 15:
        i = int(card_id[13:15])
        j = 1
    elif len(card_id) == 19:
        i = int(card_id[13:15])
        j = int(card_id[16:19])
    else:
        i = int(card_id[13:15])
        j = int(card_id.split("=")[1])
    card = cipac.Card("http://localhost/" + card_id[0:12], i, j)
    return render_template("card.j2", card=card)



# @app.route('/upload')
# def upload_file():
#     return render_template('upload.html')

# @app.route('/uploader', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         f = request.files['file']
#         f.save(secure_filename(f.filename))
#         return 'file uploaded successfully'

# @app.route('/cards/<strig:card_id>')
# def hello_user(name):
#     if name == 'admin':
#         return redirect(url_for('hello_admin'))
#     else:
#         return redirect(url_for('hello_guest', guest=name))
# vistas


# @app.route("/cipac/<string:slug>/")
# def show_post(slug):
#     slug = slug + "00"
#     return render_template("post_view.html", slug_title=slug)


# @app.route("/admin/post/")
# @app.route("/admin/post/<int:post_id>/")
# def post_form(post_id=None):
#     return render_template("admin/post_form.html", post_id=post_id)

# @app.route("/signup/", methods=["GET", "POST"])
# def show_signup_form():
#     return render_template("signup_form.html")

# @app.route("/cipac/", methods=["GET", "POST"])
# def show_cipac_menu(catalog=None):
#     return render_template("menu.html",catalog=catalog)

# @app.route("/card/<str:card_id>/", methods=["GET", "POST"])
# def show_card(card_id= None):
#     return render_template("card.html",card_id = card_id)

if __name__ == '__main__':
    app.run()
