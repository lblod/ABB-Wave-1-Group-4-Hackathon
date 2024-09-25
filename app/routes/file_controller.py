
from fastapi import APIRouter


import requests
import fitz
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from io import BytesIO
import json

router = APIRouter()

# Define a model to accept a URL input as JSON
class URLInput(BaseModel):
    url: HttpUrl  # This will ensure the input is a valid URL

@router.post("/summarize_pdf")
async def summarize_pdf(url_input: URLInput):
    try:
        # Fetch the PDF from the URL
        pdf_url = url_input.url 
        response = requests.get(pdf_url)
        response.raise_for_status()  # Check if the request was successful

        # Read the PDF content using PyMuPDF
        pdf_file = BytesIO(response.content)  # Create a file-like object
        pdf_document = fitz.open(stream=pdf_file, filetype="pdf")
        pages_text = [pdf_document.load_page(page_num).get_text("text") for page_num in range(pdf_document.page_count)]
        pdf_document.close()

        url =  'http://llm:80/summarize' # 'http://llm:80/summarize'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            "text": ''.join(pages_text)
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}")
            raise ValueError('Request failed')
                

        
    except:
        raise ValueError('Invalid URL')
    
@router.post("/process_tasks")
async def process_tasks():
        
        url = 'http://llm:80/tasks' # 'http://llm:80/tasks'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            "limit": 2
        }

        response = requests.get(url, headers=headers, params=data)

        if response.status_code == 200:
            tasks = response.json()
            url = 'http://llm:80/tasks/results' # 'http://hackathon-ai-4.s.redhost.be:2000/tasks/results'
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }

            for i,task in enumerate(tasks):
                url_input_instance = URLInput(url=task.get('downloadLink'))
                summary = await summarize_pdf(url_input=url_input_instance)
                summary = json.loads(summary)
                tasks[i]['summary'] = summary['summary']
                data = {
                    "body": tasks[i]['summary'],
                    "motivation": "nill",
                    "annotation_type": "summary",
                    "besluit_uri": tasks[i]['uri']
                    }
                response = requests.post(url, headers=headers, json=data)
            
