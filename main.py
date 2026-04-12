from flask import Flask, render_template, redirect, url_for
from routers import learning_bp, add_word_bp

app = Flask(__name__)


app.register_blueprint(learning_bp)
app.register_blueprint(add_word_bp)

@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def not_found(_error):
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
