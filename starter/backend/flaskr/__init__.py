import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import collections
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# pagination (every 10 questions). 
def paginate_questions(request , selection):
    page = request.args.get('page' ,1 ,type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  CORS(app,resources={r"/api/*":{"origins": "*"}}) 
  
  # @TODO: Use the after_request decorator to set Access-Control-Allow
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'PUT,GET,PATCH,POST,DELETE,OPTIONS')
    return response
  '''
  _________________________GET categories___________________________
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories') 
  def get_categories():
    categories = Category.query.order_by(Category.type).all()
    if len(categories) == 0 :
      abort(404)

    return jsonify({
      'success':True,
      'categories':{category.id: category.type for category in categories} 
      })
  
  '''
  ______________________________GET questions __________________________________________
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions,( current category, categories.) 
  '''
  @app.route('/questions')
  def get_questions():

        questions = Question.query.all()
        formatted_questions = paginate_questions(request, questions)

        categories = Category.query.all()
        categories_dictionary = {}
        categories_dictionary = collections.defaultdict(list)

        for category in categories:
            categories_dictionary[category.id].append(category.type)

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'categories': categories_dictionary
        })

#   '''
#   TEST: At this point, when you start the application
#   you should see questions and categories generated,
#   ten questions per page and pagination at the bottom of the screen for three pages.
#   Clicking on the page numbers should update the questions. 
#   '''


# #_________________________________DELETE METHOD________________________________________________
#   # @TODO: 
#   # Create an endpoint to DELETE question using a question ID. 
  @app.route('/questions/<int:question_id>' , methods=['DELETE'])
  def delete_questions(question_id):

    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
          abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      formatted_questions  = paginate_questions(request, selection)

      return jsonify({
        'success':True, 
        'deleted':question_id ,
        'questions' :formatted_questions ,
        'total_questions': len(selection) ,
      })

    except:
        abort(422)



#   # TEST: When you click the trash icon next to a question, the question will be removed.
#   # This removal will persist in the database and when you refresh the page. 
#   '''      
#_____________________________POST method_____________________________________

#   # '''
#   # @TODO: 
#   # Create an endpoint to POST a new question, 
#   # which will require the question and answer text, 
#   # category, and difficulty score.

  @app.route('/questions', methods=['POST']) 
  def create_question():

    data = request.get_json()
    new_question = data.get('question' ,None)
    new_answer = data.get('answer' ,None)
    new_category = data.get('category' ,None)
    new_difficulty = data.get('difficulty' ,None)
    if ((new_question is None) or (new_answer is None) or (new_difficulty is None) or (new_category is None)):
          abort(422)


    try:
       
      new_question = Question(question=new_question, answer=new_answer, category=new_category , difficulty=new_difficulty )
      new_question.insert()
        
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success':True, 
        'created': new_question.id ,
        'question': current_questions,
        'total_questions': len(Question.query.all())
      })

    except:
      abort(422)


#   # TEST: When you submit a question on the "Add" tab, 
#   # the form will clear and the question will appear at the end of the last page
#   # of the questions list in the "List" tab.  
#   # '''
#_____________________________POST methods search________________________________________________
#   # '''
#   # @TODO: 
#   # Create a POST endpoint to get questions based on a search term. 
#   # It should return any questions for whom the search term 
#   # is a substring of the question. 
  @app.route('/questions/search', methods=['POST']) 
  def search_question():
    if (request.get_json().get('searchTerm') != ""):
        search_term = request.get_json().get('searchTerm')

    if search_term:
        results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).order_by(Question.id).all()

        formatted_questions = paginate_questions(request, results)
        
        return jsonify({
              'success': True,
              'questions': formatted_questions ,
              'total_questions': len(results),
             
         })
    abort(404)
#   # TEST: Search by any phrase. The questions list will update to include 
#   # only question that include that string within their question. 
#   # Try using the word "title" to start. 
#   # '''
#_________________________________________ GET methods based on category._______________________________
#   # '''
#   # @TODO: 
#   # Create a GET endpoint to get questions based on category. 
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
      
      try:
          category = Category.query.filter(Category.id == category_id).one_or_none()
          questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
    
          question = []
          for q in questions:
              question.append(q.format())

          return jsonify({
              'success': True,
              'questions': question ,
              'total_questions': len(question),
              'current_category': category.type
          })
      except:
          abort(404)

  
  # TEST: In the "List" tab / main screen, clicking on one of the 
  # categories in the left column will cause only questions of that 
  # category to be shown. 
  # # '''
  # _________________________________________ POST methods quizzes_________________________________
  # '''
  # @TODO: 
  # Create a POST endpoint to get questions to play the quiz. 
  # This endpoint should take category and previous question parameters 
  # and return a random questions within the given category, 
  # if provided, and that is not one of the previous questions. 
  @app.route('/quizzes', methods=['POST'])
  def quiz_play():

    body=request.get_json()
    previous_question=body['previous_questions']
    category=body['quiz_category']

    if (category is None) or (previous_question is None):
      abort (400)

 
    if category['id']==0:
      questions_dictionary=Question.query.all()
    else:
      questions_dictionary=Question.query.filter_by(category=category['id']).all()
    
    total_questions=len(questions_dictionary)

    random_question = questions_dictionary[random.randrange(0, total_questions, 1)]

    def check_is_used(question):
      used=False
      for previous in previous_question:
        if (previous ==question.id):
          used=True
     
      return used


    while(check_is_used(random_question)):
      random_question = questions_dictionary[random.randrange(0,total_questions, 1)]

      if (len(previous_question)== len(questions_dictionary)):
        return jsonify ({
          'success':True ,
          'question':"null"
        })
    
    return jsonify({
      'success':True,
      'question':random_question.format()
    })



  
#   # TEST: In the "Play" tab, after a user selects "All" or a category,
#   # one question at a time is displayed, the user is allowed to answer
#   # and shown whether they were correct or not. 
#   # '''


#   # '''
#   # @TODO: 
# #   # Create error handlers for all expected errors 
# # #   # including 404 and 422. 
  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
           'success': False,
           'error': 404,
           'message': "resource not found"
        }),404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
         'success': False,
         'error': 422,
         'message': "unprocessable"
        }),422
      
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
         'success': False,
         'error': 400,
         'message': "bad request"
      }),400

  @app.errorhandler(405)
  def not_found(error):
      return jsonify({
         'success': False,
         'error': 405,
         'message': "method not allowed"
      }),405

    
  return app

    #   