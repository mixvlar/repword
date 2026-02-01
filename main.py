from flask import Flask, render_template
from routers import learning_bp, add_word_bp

app = Flask(__name__)


app.register_blueprint(learning_bp)
app.register_blueprint(add_word_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
