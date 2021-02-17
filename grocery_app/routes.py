from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date, datetime
from grocery_app.models import GroceryStore, GroceryItem, User
from grocery_app.forms import GroceryStoreForm, GroceryItemForm, LoginForm, SignUpForm

# Import app and db from events_app package so that we can run app
from grocery_app import app, db, bcrypt

main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__)

##########################################
#           Routes                       #
##########################################



@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Account Created')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.homepage'))
    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.homepage'))













@main.route('/')
def homepage():
    all_stores = GroceryStore.query.all()
    print(all_stores)
    return render_template('home.html', all_stores=all_stores)


@main.route('/new_store', methods=['GET', 'POST'])
@login_required
def new_store():
    form = GroceryStoreForm()

    if form.validate_on_submit():
        new_grocery_store = GroceryStore(
            title=form.title.data,
            address=form.address.data,
            created_by=current_user
        )
        db.session.add(new_grocery_store)
        db.session.commit()

        flash('New book was created successfully.')
        return redirect(url_for('main.store_detail', store_id=new_grocery_store.id))
    return render_template('new_store.html', form=form)


@main.route('/new_item', methods=['GET', 'POST'])
@login_required
def new_item():
    form = GroceryItemForm()

    if form.validate_on_submit():
        new_store_item = GroceryItem(
            name=form.name.data,
            price=form.price.data,
            category=form.category.data,
            photo_url=form.photo_url.data,
            store=form.store.data,
            created_by=current_user
        )
        db.session.add(new_store_item)
        db.session.commit()

        flash('New item was created successfully.')
        return redirect(url_for('main.item_detail', item_id=new_store_item.id))
    return render_template('new_item.html', form=form)


@main.route('/store/<store_id>', methods=['GET', 'POST'])
@login_required
def store_detail(store_id):
    store = GroceryStore.query.get(store_id)
    created_by_user = User.query.get(store.created_by_id)

    form = GroceryStoreForm(obj=store)
    if form.validate_on_submit():
        store.title = form.title.data
        store.address = form.address.data

        db.session.add(store)
        db.session.commit()

        flash('Book updated successfully.')
        return redirect(url_for('main.store_detail', store_id=store.id))

    store = GroceryStore.query.get(store_id)
    return render_template('store_detail.html', store=store, created_by_user=created_by_user, form=form)


@main.route('/item/<item_id>', methods=['GET', 'POST'])
@login_required
def item_detail(item_id):
    item = GroceryItem.query.get(item_id)
    created_by_user = User.query.get(item.created_by_id)

    form = GroceryItemForm(obj=item)

    if form.validate_on_submit():
        item.name = form.name.data
        item.price = form.price.data
        item.category = form.category.data
        item.photo_url = form.photo_url.data
        item.store = form.store.data

        db.session.add(item)
        db.session.commit()

        flash('Item updated successfully.')
        return redirect(url_for('main.item_detail', item_id=item.id))

    item = GroceryItem.query.get(item_id)
    return render_template('item_detail.html', item=item, created_by_user=created_by_user, form=form)

@main.route('/shopping_list', methods=['GET'])
@login_required
def shopping_list():
    user = User.query.get(current_user.id)

    return render_template('shopping_list.html', user=user)


@main.route('/add_to_shopping_list/<item_id>', methods=['POST'])
@login_required
def add_to_shopping_list(item_id):
    user = User.query.get(current_user.id)
    item = GroceryItem.query.get(item_id)
    created_by_user = User.query.get(item.created_by_id)

    user.shopping_list_items.append(item)
    db.session.add(user)
    db.session.commit()

    flash('Item added to your cart successfully.')
    return redirect(url_for('main.item_detail', item_id=item.id))

