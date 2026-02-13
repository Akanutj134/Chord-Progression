from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    """Main page with links to different tools."""
    return render_template('index.html')

@app.route('/quiz')
def mini_quiz():
    """Redirects to the Mini Quiz."""
    return render_template('quiz.html')

@app.route('/game')
def game():
    """Serve the game page inside the website."""
    return render_template('game.html')

if __name__ == '__main__':
    app.run(port=5001, debug=True)  
