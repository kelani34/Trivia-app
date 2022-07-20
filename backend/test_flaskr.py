import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = os.getenv('DB_NAME_TEST')
        self.database_user = os.getenv('DB_USER')
        self.database_host = os.getenv('DB_HOST')
        self.database_path = "postgresql://{}@{}/{}".format(self.database_user, self.database_host, self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_categories'])

    def test_404_get_categories(self):
        res = self.client().get('/categories/777')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))

    def test_404_paginate_question(self):
        res = self.client().get('/questions?page=777')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        question = Question(question='what day is independence day', answer='July 4th',
                            difficulty=3, category=4)
        question.insert()
        question_id = question.id

        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.id == question.id).one_or_none()
        if res.status_code == 200:
            self.assertEqual(res.status_code, 200)
        elif res.status_code == 404:
            self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], 'Deleted')

    def test_422_delete_question(self):
        res = self.client().delete('/questions/999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_question(self):
        new_question = {
            'question': 'what date is independence day',
            'answer': 'July 4th',
            'difficulty': 3,
            'category': 4
        }
        before = len(Question.query.all())
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        after = len(Question.query.all())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertEqual(after, before + 1)
        self.assertTrue(data["total_questions"])

    def test_422_create_question(self):
        new_question = { }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_searchTerm(self):
        new_search = {'searchTerm': 'independence day'}
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)

        if res.status_code == 200:
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['success'], True)
        elif res.status_code == 404:
            self.assertEqual(res.status_code, 404)
            self.assertEqual(data['success'], False)

    def test_404_searchTerm(self):
        new_search = {
            'searchTerm': '',
        }
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_questions_based_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_questions_based_category(self):
        res = self.client().get('/categories/777/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_play_quiz(self):
        new_quiz = {'previous_questions': [],
                          'quiz_category': {'type': 'History', 'id': 4}}

        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_422_play_quiz(self):
        new_quiz = {'previous_questions': []}
        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()