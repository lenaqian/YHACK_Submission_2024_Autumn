from sentence_transformers import SentenceTransformer
from create_table import create_courses_table
from sqlalchemy import create_engine
from flask import Flask, request
from flask_cors import CORS
from dotenv import load_dotenv
import pandas as pd
import tools
import os

load_dotenv()

app = Flask(__name__)
CORS(app)
API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise ValueError("No API key set for the application!")

# load model (for generating description vectors)
model = SentenceTransformer('all-MiniLM-L6-v2') 

@app.route('/')
def home():
    return 'Welcome to flask!'

@app.route('/get-subjects', methods=['GET'])
def get_subjects():
    return tools.get_subjects_api_call(API_KEY)
    
@app.route('/get-subject-info', methods=['GET'])
def get_subject_info():
    return tools.get_subjects_info_api_call(API_KEY, 'ENGL')

@app.route('/search', methods=['GET'])
def search_courses():

    # data = request.json
    description_search = request.args.get('query')
    department = request.args.get('department')

    return tools.perform_search(model, engine, description_search, department)

if __name__ == '__main__':

    username = 'demo'
    password = 'demo'
    hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
    port = '1972' 
    namespace = 'USER'
    CONNECTION_STRING = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"
    engine = create_engine(CONNECTION_STRING)
    df = pd.read_csv('clean_courses.csv')
    
    #create embeddings
    embeddings = model.encode(df['description'].tolist(), normalize_embeddings=True)
    # add the embeddings to the DataFrame
    df['description_vector'] = embeddings.tolist()

    create_courses_table(df, engine)
    app.run(debug=True)


