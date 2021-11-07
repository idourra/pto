from flask import Flask
from flask import render_template
from files4libs import cipac

app = Flask(__name__)

app.config['DEBUG']


#card = cipac.Card("bnjmsculyfof0010001","http://bnjm.sld.cu/bnjmsculyfof","/home/urra/projects/pto/tests/data/bdc/bnjm/bnjmsculyfof")
catalog = cipac.Catalog("bnjmsculyfof","http://bnjm.sld.cu/bnjmsculyfof","/home/urra/projects/pto/tests/data/bdc/bnjm/bnjmsculyfof")


@app.context_processor
def provide_catalog():
    catalog = cipac.Catalog("bnjmsculyfof","http://bnjm.sld.cu/bnjmsculyfof","/home/urra/projects/pto/tests/data/bdc/bnjm/bnjmsculyfof")
    return {'catalog':catalog}


@app.route("/")
def home():
    return render_template("base_template.html",catalog=catalog)


@app.route("/about")
def about():
    #return "{} Catalog has {} cards in {} drawers".format(catalog.id,catalog.q_cards,catalog.q_drawers)
    return render_template("about.html",catalog=catalog)


@app.route("/cards/<string:card_id>/")
def show_card(card_id):
    if len(card_id) == 12:
        card_id = card_id + "0010001"
    elif len(card_id) == 15:
        card_id = card_id + "0001"
    card = cipac.Card(card_id,"http://bnjm.sld.cu/"+ card_id[:12],"")
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

@app.route("/cipac/", methods=["GET", "POST"])
def show_cipac_menu(catalog=None):
    return render_template("menu.html",catalog=catalog)

# @app.route("/card/<str:card_id>/", methods=["GET", "POST"])
# def show_card(card_id= None):
#     return render_template("card.html",card_id = card_id)

