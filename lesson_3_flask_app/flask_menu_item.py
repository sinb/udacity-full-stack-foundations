# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/hello')
def HelloWorld():
    restaurant_1 = session.query(Restaurant).first()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_1.id)
    output = ""
    for item in items:
        output += item.name
        output += "</br>"
        output += item.price
        output += "</br>"
        output += item.description
        output += "</br>"
        output += "</br>"
    return output


@app.route("/restaurant/<int:restaurant_id>/")
def restaurantMenu(restaurant_id):
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    except:
        return "No data return"
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template("menu.html", restaurant=restaurant, items=items)


@app.route('/restaurant/<int:restaurant_id>/new/', methods=["POST", "GET"])
def newMenuItem(restaurant_id):
    if request.method == "POST":
        menuItem = MenuItem(name=request.form['name'], restaurant_id=restaurant_id)
        session.add(menuItem)
        session.commit()
        flash("new item created!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template("newmenuitem.html", restaurant_id=restaurant_id)

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/', methods=["POST", "GET"])
def editMenuItem(restaurant_id, menu_id):
    thisMenuItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == "POST":
        pass
        thisMenuItem.name = request.form['name']
        session.add(thisMenuItem)
        session.commit()
        flash("item: %s edited!" % thisMenuItem.name)
        return redirect(url_for("restaurantMenu", restaurant_id=restaurant_id))
    else:
        return render_template("editmenuitem.html", restaurant_id=restaurant_id, menu_id=menu_id, item=thisMenuItem)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/', methods=["POST", "GET"])
def deleteMenuItem(restaurant_id, menu_id):
    thisMenuItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(thisMenuItem)
        session.commit()
        flash("item: %s deleted!" % thisMenuItem.name)
        return redirect(url_for("restaurantMenu", restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=thisMenuItem)


@app.route('/restaurant/<int:restaurant_id>/menu/JSON/')
def restaurantMenuJSON(restaurant_id):
    thisRrstaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def restaurantMenuOneJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItems=item.serialize)

if __name__ == '__main__':
    app.secret_key = "my_secret_key"
    app.debug = True
    app.run(host='127.0.0.1', port=5000)
