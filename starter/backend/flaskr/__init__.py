import os
from flask import Flask, request, abort, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import collections
from models import setup_db, Question, Category, db
from sqlalchemy import func

QUESTIONS_PER_PAGE = 10

# pagination (every 10 questions)


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # @TODO: Set up CORS.
    # Allow '*' for origins.
    # Delete the sample route after completing the TODOs
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    # @TODO: Use the after_request decorator to set Access-Control-Allow

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'PUT,GET,PATCH,POST,DELETE,OPTIONS')
        return response
    # (GET categories)
    # @TODO:
    # Create an endpoint to handle GET requests
    # for all available categories.

    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.type).all()
        if len(categories) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'categories': {category.id: category.type
                           for category in categories}
                        })
    # (GET questions)
    # @TODO:
    # Create an endpoint to handle GET requests for questions
    # including pagination (every 10 questions)
    # This endpoint should return a list of questions
    # number of total questions,( current category, categories.)

    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        formatted_questions = paginate_questions(request, questions)
        categories = Category.query.order_by(Category.type).all()
        if len(formatted_questions) == 0:
            abort(404)
            return jsonify({
                'success': False
                })
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'categories': {category.id: category.type
                           for category in categories},
            'current_category': None
            })
    # TEST: At this point, when you start the application
    # you should see questions and categories generated
    # ten questions per page and pagination at
    # the bottom of the screen for three pages
    # Clicking on the page numbers should update the questions
    # (DELETE METHOD)
    #  @TODO:
    #  Create an endpoint to DELETE question using a question ID

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        question = db.session.query(Question).get(question_id)
        if(question) is None:
            abort(422)
        else:
            try:
                question.delete()
            except SQLAlchemyError as e:
                print(e)
                db.session.rollback()
            finally:
                db.session.close()
            return jsonify({
                "success": True,
                "deleted": question_id
                })
    # TEST: When you click the trash icon next to a question
    # the question will be removed
    # This removal will persist in the database
    # and when you refresh the page
    # (POST method)
    # @TODO:
    # Create an endpoint to POST a new question
    # which will require the question and answer text
    # category, and difficulty score

    @app.route('/questions', methods=['POST'])
    def create_question():
        data = request.get_json()
        ques = data.get('question')
        answer = data.get('answer')
        difficulty = data.get('difficulty')
        category = data.get('category')
        new_question = Question(
                       question=ques,
                       answer=answer,
                       category=category,
                       difficulty=difficulty
                        )
        new_question_id = new_question.id
        try:
            new_question.insert()
            new_question_id = new_question.id
        except Exception:
            abort(422)
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({
            "success": True,
            "created": new_question_id
            })
    # TEST: When you submit a question on the "Add" tab
    # the form will clear and the question will appear
    # at the end of the last page
    # of the questions list in the "List" tab
    # (POST methods search)
    # @TODO:
    # Create a POST endpoint to get questions based on a search term
    # It should return any questions for whom the search term
    # is a substring of the question

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        if (request.get_json().get('searchTerm') != ""):
            search_term = request.get_json().get('searchTerm')
        if search_term:
            results = Question.query.filter(
                        Question.question.ilike(f'%{search_term}%')
                        ).order_by(Question.id).all()
            return jsonify({
                'success': True,
                'questions': [question.format() for question in results],
                'total_questions': len(results),
                })
        abort(404)
    # TEST: Search by any phrase. The questions list will update to include
    # only question that include that string within their question
    # Try using the word "title" to start
    # (GET methods based on category.)
    # @TODO:
    # Create a GET endpoint to get questions based on category

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            category = Category.query.filter(
                       Category.id == category_id
                       ).one_or_none()
            questions = Question.query.filter(
                        Question.category == category_id
                      ).order_by(Question.id).all()

            question = []
            for q in questions:
                question.append(q.format())
            return jsonify({
                'success': True,
                'questions': question,
                'total_questions': len(question),
                'current_category': category.type
                })
        except Exception:
            abort(404)
    # TEST: In the "List" tab / main screen, clicking on one of the
    # categories in the left column will cause only questions of that
    # category to be shown
    # (POST methods quizzes)
    # @TODO:
    # Create a POST endpoint to get questions to play the quiz
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category
    # if provided, and that is not one of the previous questions

    @app.route('/quizzes', methods=['POST'])
    def test_quiz_play():
        body = request.get_json()
        if not ('quiz_category' in body and 'previous_questions' in body):
            abort(422)
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')

        try:
            category_id = quiz_category['id']
            if category_id == 0:
                selection = Question.query.filter(
                        Question.id.notin_((previous_questions))).all()
            else:
                selection = Question.query.filter(
                    Question.category == category_id).filter(
                        Question.id.notin_((previous_questions))).all()

            new_question = random.choice(selection)
            avilable_question = len(selection)
            if avilable_question > 0:
                return jsonify({
                    "success": True,
                    "question": new_question.format()
                })
            else:
                return jsonify({
                    "success": True,
                    "question": None
                })
        except Exception:
            abort(422)
    # TEST: In the "Play" tab, after a user selects "All" or a category
    # one question at a time is displayed, the user is allowed to answer
    # and shown whether they were correct or not
    # @TODO:
    # Create error handlers for all expected errors
    # including 404 and 422

    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "resource not found"
            }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "unprocessable"
            }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "bad request"
            }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "method not allowed"
            }), 405
    return app
