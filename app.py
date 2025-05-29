from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Question, Option, Score
import random


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'JORGERUEDA123'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    top_scores = []

    if request.method == 'POST':
        username = request.form.get('username')
        subject = request.form.get('subject')
        correct = 0
        bonus_time = 0.0

        question_ids = session.get('question_order', [])
        questions = [Question.query.get(qid) for qid in question_ids]

        for question in questions:
            q_id = question.id
            opt_key = f'question_{q_id}'
            time_key = f'time_q{q_id}'

            option_id_str = request.form.get(opt_key, "")
            time_str = request.form.get(time_key, "0")

            if option_id_str.strip().isdigit():
                option_id = int(option_id_str)
                selected_option = Option.query.get(option_id)

                if selected_option and selected_option.is_correct:
                    correct += 1
                    try:
                        seconds = int(time_str)
                        bonus = max(0, 1 - (seconds / 30))
                        bonus_time += bonus
                    except ValueError:
                        pass

        try:
            final_score = float(request.form.get('final_score', 0))
        except ValueError:
            final_score = 0

        new_score = Score(username=username, subject=subject, score=final_score)
        db.session.add(new_score)
        db.session.commit()

        top_scores = Score.query.filter_by(subject=subject).order_by(Score.score.desc()).limit(5).all()

        # Limpia datos de sesión al finalizar
        session.pop('question_order', None)
        session.pop('subject', None)

        return render_template(
            'quiz.html',
            questions=[],
            top_scores=top_scores,
            quiz_completed=True,
            subject=subject,
            username=username
        )

    # GET method
    subject = request.args.get('subject')
    username = request.args.get('username')

    # Si el subject cambió, reiniciar orden de preguntas
    if subject and session.get('subject') != subject:
        session.pop('question_order', None)
        session['subject'] = subject

    questions = []
    if subject:
        if 'question_order' not in session:
            all_questions = Question.query.filter_by(subject=subject).all()
            question_ids = [q.id for q in all_questions]
            random.shuffle(question_ids)
            session['question_order'] = question_ids

        question_ids = session['question_order']
        questions = [Question.query.get(qid) for qid in question_ids]
        top_scores = Score.query.filter_by(subject=subject).order_by(Score.score.desc()).limit(5).all()

    return render_template(
        'quiz.html',
        questions=questions,
        top_scores=top_scores,
        quiz_completed=False,
        subject=subject,
        username=username
    )


if __name__ == '__main__':
    app.run(debug=True)
