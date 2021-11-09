from flask import Flask
from flask import render_template
from files4libs import cipac

app = Flask(__name__)

app.config['DEBUG']


catalog = cipac.Catalog("http://localhost/bnjmsculyfof")


@app.context_processor
def provide_catalog():
    catalog = cipac.Catalog("http://localhost/bnjmsculyfof")
    return {'catalog':catalog}


@app.route("/")
def home():
    return render_template("base_template.html",catalog=catalog)


@app.route("/about")
def about():
    #return "{} Catalog has {} cards in {} drawers".format(catalog.id,catalog.q_cards,catalog.q_drawers)
    return render_template("about.html",catalog=catalog)


@app.route("/<string:cipac_id>/")
def show_catalog(cipac_id):
    if len(cipac_id) == 12:
        i = 1
        j = 1
    else:
        i = int(cipac_id[13:15])
        j = int(cipac_id[16:19])
    card = cipac.Card("http://localhost/" + cipac_id[0:12],i, j  )
    return render_template("card.html",card = card)

@app.route("/cards/<string:card_id>/")
def show_card(card_id):
    if len(card_id) == 12:
        card_id = card_id + "0010001"
    elif len(card_id) == 15:
        card_id = card_id + "0001"
    card = cipac.Card("http://localhost/" + card_id[0:12],int(card_id[13:15]), int(card_id[16:19])  )
    return render_template("card.html",card = card)


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

