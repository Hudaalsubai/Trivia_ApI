import os
import unittest
import json
import tempfile
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
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','1234','localhost:5432',self.database_name)


        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is the captial city  of Saudi Arabia',
            'answer': 'Riyadh ',
            'difficulty': 3,
            'category': 4
        }

        self.new_search = {
            'searchTerm': 'A'
        }


        self.new_quiz_round = {
             'previous_questions': [],
             'quiz_category': {'type': 'Art', 'id': 2

        }}
        self.new_question_error = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1
        }


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()



            
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    
    # """
    # TODO
    # Write at least one test for each test for successful operation and for expected errors.
    # # """
    #_____________________________________________/questions________________
    def test_get_paginated_questions(self): 
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    
  
    def test_404_sent_requesting_questions_beyond_vaild_page(self): 
        res = self.client().get('/questions?page=100') 
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    #_______________________________________/categories___________________________________
    def test_get_categories(self): 
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_non_existing_category(self):
        res = self.client().get('/categories/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    #_______________________________________/quethions DELETE___________________________________
    def test_delete_question(self): 
        question = Question(question='new question', answer='new answer',
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id

        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.id == question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertEqual(question, None)


    def test_404_if_question_does_no_resource(self): 
        res = self.client().delete('/questions/')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


# #_______________________________________/quetionss CREATE___________________________________
    def test_create_question(self):
     
        total_questions_before = len(Question.query.all())
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        total_questions_after = len(Question.query.all())


        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_questions_after, total_questions_before + 1)



# #_______________________________________/questions SEARCH___________________________________

    def test_search_questions(self):

  
        res = self.client().post('/questions/search', json=self.new_search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

# # #_______________________________________/questions  get ___________________________________

    def test_get_questions_per_category(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Geography')


    def test_404_get_questions_per_category_not_found(self):
        res = self.client().get('/categories/b/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

# #_______________________________________/quizzes PLAY POST ___________________________________

    def test_quiz_play(self):
    

        res = self.client().post('/quizzes', json=self.new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data["question"])


    def test_422_play_quiz(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
