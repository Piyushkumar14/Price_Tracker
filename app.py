from flask import Flask, request, render_template, redirect, url_for, flash
from price_tracker.price_tracker import check_prices as main

app = Flask(__name__)
# app.secret_key = 'your_secret_key' # Set a secret key for flashing messages


@app.route('/', methods=['GET', 'POST'])
def index():
    product_data = None
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_data = main(product_name)
        if not product_data:
            flash("No product found with the provided name.")
            return redirect(url_for('index'))
        flash("Price check complete.")
    return render_template('webapp/index.html', product_data=product_data)


if __name__ == "__main__":
    app.run(debug=True)
