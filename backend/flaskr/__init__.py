import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10

# paginate each pages to render 10 question on each page
# From the QUESTIONS_PER_PAGE constant


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_question = questions[start:end]

    return current_question
# organize each categories to match 'id': 'type'


def converted_categories():
    categories = Category.query.all()
    dict = {}
    for category in categories:
        dict[category.id] = category.type
    return dict


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # set up CORS, allowing all origins
    CORS(app, resources={'/': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        '''
        Sets access control.
        '''
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,DELETE,PUT,OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        ''' Render the data for all categories'''
        categories = converted_categories()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories,
            "total_categories": len(Category.query.all()),
        })

    @app.route('/questions')
    def get_questions():
        ''' Render Questions based on each categories'''
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)
        categories = converted_categories()

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        ''' Renders Delete for a particular question'''
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selection)

            return jsonify(
                {
                    'success': 'Deleted',
                    'deleted': question_id,
                    'question': current_question,
                    'total_question': len(Question.query.all())}
            )
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        ''' Renders avalability to create new questions'''
        body = request.get_json()

        new_category = body.get('category')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_question = body.get('question')
        if new_question is None or new_answer is None or new_category is None or new_difficulty is None:
            abort(422)
        searchTerm = body.get('searchTerm')

        try:
            if searchTerm:
                selection = Question.query.filter(
                    Question.question.ilike(f'%{searchTerm}%')).all()

                if len(selection) == 0:
                    abort(404)

                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
            else:
                question = Question(
                    category=new_category,
                    answer=new_answer,
                    question=new_question,
                    difficulty=new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                if new_question is None or new_answer is None or new_category is None or new_difficulty is None:
                    abort(422)
                current_question = paginate_questions(request, selection)

                return jsonify(
                    {
                        'success': True,
                        'created': question.id,
                        'question_created': question.question,
                        'question': current_question,
                        'total_questions': len(Question.query.all()),
                    }
                )
        except:
            abort(422)

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_based_category(category_id):
        ''' Renders all qiestions in a particular category'''

        category = Category.query.filter(
            category_id == Category.id).one_or_none()
        if category is None:
            abort(404)

        selection = Question.query.filter(
            Question.category == category.id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        ''' Renders availability to random questions '''

        body = request.get_json()
        previous_questions = body.get('previous_questions')
        if previous_questions is None:
            abort(422)
        quiz_category = body.get('quiz_category')
        if quiz_category is None:
            abort(422)

        if quiz_category['id'] == 0:
            questions = Question.query.all()

        else:
            questions = Question.query.filter_by(
                category=quiz_category['id']).all()
        random_question = questions[random.randrange(
            0, len(questions), 1)].format()
        question = random_question
        checked = False

        for i in previous_questions:
            # print(question)
            if i == question['id']:
                checked = True

        while checked:
            question = random_question
            if len(previous_questions) == len(questions):
                return jsonify({
                    'success': True
                })

        return jsonify({
            'success': True,
            'question': question
        })

    # Error handllerss for each error that may occur
    @app.errorhandler(404)
    def handle_not_found_error404(e):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(400)
    def handle_bad_request_error400(e):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(422)
    def handle_unprocessable_error422(e):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    return app
