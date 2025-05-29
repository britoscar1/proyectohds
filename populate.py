import json
from pathlib import Path
from app import app, db
from models import Question, Option

json_path = Path(__file__).parent / "preguntas.json"

with app.app_context():
  
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)


    Option.query.delete()
    Question.query.delete()
    db.session.commit()


    for materia, preguntas in data.items():
        for item in preguntas:
            question = Question(text=item["question"], subject=materia)  # <-- añadimos subject aquí
            db.session.add(question)
            db.session.flush()  # obtener ID de pregunta

            for opt in item["options"]:
                option = Option(
                    text=opt,
                    is_correct=(opt == item["answer"]),
                    question_id=question.id
                )
                db.session.add(option)

    db.session.commit()
    print("Base de datos actualizada con preguntas desde preguntas.json.")
