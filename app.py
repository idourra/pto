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

@app.context_processor
def alphabet():
    return {'abcd' : ["A","B","C","D","E","F","G","H"]}

@app.route("/")
def home():
    return render_template("base_template.html",catalog=catalog)


@app.route("/about")
def about():
    #return "{} Catalog has {} cards in {} drawers".format(catalog.id,catalog.q_cards,catalog.q_drawers)
    return render_template("about.html",catalog=catalog)

# @app.route("/cards/")
# def card():
#     return render_template("card.html",catalog=catalog)

@app.route("/cards/<string:card_id>/")
def show_card(card_id):
    card = cipac.Card(card_id,catalog.url.geturl(),"")
    return render_template("card.html",card = card)

@app.route("/p/<string:slug>/")
def show_post(slug):
    return "Mostrando el post {}".format(slug)

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

