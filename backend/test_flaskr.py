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
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    def test_retrieve_categories(self):
        # get response and load data
        response = self.client().get('/categories')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that categorie return data
        self.assertTrue(data['categories'])

    def test_retrieve_questions(self):
        # get response and load data
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check questions and total_questions return data
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['total_questions'], len(Question.query.all()))

    def test_404_equest_beyond_valid_page(self):
        # send request with bad page data, load response
        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_delete_question(self):
        question = Question(question='question', answer='answer', category=1, difficulty=2)
        question.insert()

        # get the id of the new question
        q_id = question.id
        
        # get number of questions before delete
        total_questions_before_deleting = len(Question.query.all())

        # get response and load data
        response = self.client().delete('/questions/{}'.format(q_id))
        data = json.loads(response.data)
        
        # get number of questions after delete
        total_questions_after_deleting = len(Question.query.all())

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check if question id matches deleted id
        self.assertEqual(data['deleted'], q_id)

        # check that total_questions and questions return data
        self.assertTrue(data['questions'])
        self.assertEqual(data['total_questions'],
                         total_questions_before_deleting-1)

        # check if one less question after delete
        self.assertTrue(total_questions_before_deleting - total_questions_after_deleting == 1)

    def test_create_questions(self):
        new_question = {
            'question' : 'Test new question',
            'answer' : 'Test answer',
            'difficulty' : 1,
            'category' : 1
        }
        total_questions_before_creating = len(Question.query.all())

        # post response and load data
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        total_questions_after_creating = len(Question.query.all())

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        
        # check if one less question before create new question
        self.assertTrue(total_questions_after_creating - total_questions_before_creating == 1)
    
    def test_422_if_question_creation_fails(self):
        # get number of questions before post
        total_questions_before_creating = len(Question.query.all())

        # create new question without json data, then load response data
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        # get number of questions after post
        total_questions_after_creating = len(Question.query.all())

        # check status code and success message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

        # check if questions_after and questions_before are equal
        self.assertTrue(total_questions_after_creating == total_questions_before_creating)


    def test_search_questions(self):
        searchTerm = {
            'searchTerm' : 'what'
        }

        # post response and load data
        response = self.client().post('/questions', json=searchTerm)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_retrieve_questions_by_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that questions are returned (len != 0)
        self.assertNotEqual(len(data['questions']), 0)

        # check that current category returned is science
        self.assertEqual(data['current_category'], {'id': 1, 'type': 'Science'})

    def test_400_if_questions_by_category_fails(self):
        # send request with category id 100
        response = self.client().get('/categories/100/questions')

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_play_quizz(self):
        body = {
            'previous_questions': [20],
            'quiz_category': {
                'id': '1',
                'type': 'Science'
                }
        }
        # get response and load data
        response = self.client().post('/quizzes', json=body)
        data = json.loads(response.data)

        # check status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that a question is returned
        self.assertTrue(data['question'])

        # check that the question returned is in correct category
        self.assertEqual(data['question']['category'], 1)


    def test_play_quiz_fails(self):
        # send post request without json data
        response = self.client().post('/quizzes', json={})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()