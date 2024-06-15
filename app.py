import boto3
from flask import Flask, render_template, request, session
import openai
import os

app = Flask(__name__)

# Fetch environment variables from AWS Parameter Store
ssm = boto3.client('ssm', region_name='your-region')  # specify your AWS region
openai_api_key = ssm.get_parameter(Name='OPENAI_API_KEY', WithDecryption=True)['Parameter']['Value']
secret_key = ssm.get_parameter(Name='SECRET_KEY', WithDecryption=True)['Parameter']['Value']

openai.api_key = openai_api_key
app.secret_key = secret_key

# Initial questions
questions = [
    "Please provide your general information like name, city, state, country.",
    "Please provide your academic performance (grade, board, present percentage).",
    "What is your goal, financial position, and Which places are you interested in going to for studies?"
]

# Options to present after initial questions
options = [
    "Would you like a detailed roadmap to achieve your career goals considering your academics, financial status, and study locations?",
    "Do you want personalized career guidance based on your academic performance, financial status, and desired study locations?",
    "Do you need other specific guidance like scholarship opportunities, study programs, or financial planning?",
    "Other"
]

@app.route('/')
def home():
    session.clear()
    session['question_index'] = 0
    session['user_responses'] = []
    return render_template('chat.html', initial_question=questions[0])

@app.route('/process_chat', methods=['POST'])
def process_chat():
    user_input = request.form.get('user_input')
    if user_input:
        question_index = session.get('question_index', 0)
        if question_index < len(questions):
            session['user_responses'].append(user_input)
            question_index += 1
            session['question_index'] = question_index
            if question_index < len(questions):
                return questions[question_index]
            else:
                options_html = render_template('options.html', options=options)
                return options_html
        else:
            bot_response = get_ai_response(user_input)
            return bot_response
    return "Invalid input"

def get_ai_response(input_text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    # Add all user responses
    for response in session.get('user_responses', []):
        messages.append({"role": "user", "content": response})
    
    messages.append({"role": "user", "content": input_text})
    
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return completion.choices[0].message['content']

if __name__ == '__main__':
    app.run(debug=True)
