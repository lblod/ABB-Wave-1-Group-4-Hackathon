
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

## General summary
# SYS_PROMPT01 = """
#         You are an expert in summarizing text data based on a provided context. Your task is to summarize the given text provided in the context.
        
#         Summarize the document provided in context. Ensure that the summary is concise and captures the main points of the document. 
#         Keep the text in its original language and do not translate the names of people, places, or organizations.
        
#         Desired Output:
#         Output the summary in a JSON format, like this:
#         {
#             "summary": "Your summary here."
#         }
# """
SYS_PROMPT01 = """
    Je bent een expert in het samenvatten van tekstgegevens op basis van een gegeven context. Het is jouw taak om de gegeven tekst in de context samen te vatten.
        
    Vat het gegeven document samen in de context. Zorg ervoor dat de samenvatting beknopt is en de belangrijkste punten van het document weergeeft. 
    Houd de tekst in de oorspronkelijke taal en vertaal de namen van mensen, plaatsen of organisaties niet.
    
    Gewenste uitvoer:
    Voer de samenvatting uit in een JSON-indeling, zoals deze:
    {
        “samenvatting": “Uw samenvatting hier.”
    }
"""

## Allowed actions summary.
# SYS_PROMPT02 = """
#         You are an expert in summarizing text data based on a provided context. Your task is to summarize the given text provided in the context, focusing and only including the allowed actions in the summary.
        
#         Summarize the document provided in context. Ensure that the summary is concise and captures the main points of the document. 
#         Keep the text in its original language and do not translate the names of people, places, or organizations.
        
#         Desired Output:
#         Output the summary in a JSON format, like this:
#         {
#             "summary": "Your summary here."
#         }
# """
SYS_PROMPT02 = """
    Je bent een expert in het samenvatten van tekstgegevens op basis van een gegeven context. Het is jouw taak om de gegeven tekst in de context samen te vatten, waarbij je je concentreert en alleen de toegestane acties in de samenvatting opneemt.
        
    Vat het gegeven document samen in de context. Zorg ervoor dat de samenvatting beknopt is en de belangrijkste punten van het document weergeeft. 
    Houd de tekst in de oorspronkelijke taal en vertaal de namen van mensen, plaatsen of organisaties niet.
    
    Gewenste uitvoer:
    Voer de samenvatting uit in een JSON-indeling, zoals deze:
    {
        “samenvatting": “Uw samenvatting hier.”
    }
"""

## Requires permit summary.
# SYS_PROMPT03 = """
#         You are an expert in summarizing text data based on a provided context. Your task is to summarize the given text provided in the context, focusing and only including what requires a permit in the summary.
                
#         Summarize the document provided in context. Ensure that the summary is concise and captures the main points of the document. 
#         Keep the text in its original language and do not translate the names of people, places, or organizations.
        
#         Desired Output:
#         Output the summary in a JSON format, like this:
#         {
#             "summary": "Your summary here."
#         }
# """
SYS_PROMPT03 = """
    Je bent een expert in het samenvatten van tekstgegevens op basis van een gegeven context. Het is jouw taak om de gegeven tekst in de context samen te vatten, waarbij je je concentreert en alleen datgene in de samenvatting opneemt waarvoor een vergunning nodig is.
        
    Vat het gegeven document samen in de context. Zorg ervoor dat de samenvatting beknopt is en de belangrijkste punten van het document weergeeft. 
    Houd de tekst in de oorspronkelijke taal en vertaal de namen van mensen, plaatsen of organisaties niet.
    
    Gewenste uitvoer:
    Voer de samenvatting uit in een JSON-indeling, zoals deze:
    {
        “samenvatting": “Uw samenvatting hier.”
    }
"""


@router.post("/summarize_pdf")
async def summarize_pdf(url_input: URLInput, sys_prompt: str):
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

        url =  'http://llm:80/raw_prompt' # 'http://llm:80/summarize'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        data = {
            "system_message": sys_prompt,# SYS_PROMPT01,
            "prompt": ''.join(pages_text)
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
            "limit": 10
        }

        status_code = 200

        while status_code == 200:
            response = requests.get(url, headers=headers, params=data)
            if response.status_code == 200:
                status_code = response.status_code
                tasks = response.json()
                url = 'http://llm:80/tasks/results' # 'http://hackathon-ai-4.s.redhost.be:2000/tasks/results'
                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json'
                }

                for i,task in enumerate(tasks):
                    url_input_instance = URLInput(url=task.get('downloadLink'))

                    # Generic summary post
                    generic_summary = await summarize_pdf(url_input=url_input_instance, sys_prompt=SYS_PROMPT01)
                    generic_summary = json.loads(generic_summary)
                    tasks[i]['generic_summary'] = generic_summary['samenvatting']
                    generic_data = {
                        "body": tasks[i]['generic_summary'],
                        "motivation": "nill",
                        "annotation_type": "summary",
                        "besluit_uri": tasks[i]['uri']
                        }
                    response = requests.post(url, headers=headers, json=generic_data)

                    # Allowed actions summary post
                    allowed_summary = await summarize_pdf(url_input=url_input_instance, sys_prompt=SYS_PROMPT02)
                    allowed_summary = json.loads(allowed_summary)
                    tasks[i]['allowed_summary'] = allowed_summary['samenvatting']
                    allowed_data = {
                        "body": tasks[i]['allowed_summary'],
                        "motivation": "nill",
                        "annotation_type": "allowed_actions",
                        "besluit_uri": tasks[i]['uri']
                        }
                    response = requests.post(url, headers=headers, json=allowed_data)

                    # Requires permit summary post
                    permit_summary = await summarize_pdf(url_input=url_input_instance, sys_prompt=SYS_PROMPT03)
                    permit_summary = json.loads(permit_summary)
                    tasks[i]['permit_summary'] = permit_summary['samenvatting']
                    permit_data = {
                        "body": tasks[i]['permit_summary'],
                        "motivation": "nill",
                        "annotation_type": "allowed_actions",
                        "besluit_uri": tasks[i]['uri']
                        }
                    response = requests.post(url, headers=headers, json=permit_data)
            else:
                print(tasks[i])
                print('='*50,response.status_code)
                status_code = response.status_code
            
