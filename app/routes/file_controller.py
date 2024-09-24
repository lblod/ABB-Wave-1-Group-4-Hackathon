
from fastapi import APIRouter


import requests
import fitz
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from io import BytesIO

router = APIRouter()

# Define a model to accept a URL input as JSON
class URLInput(BaseModel):
    url: HttpUrl  # This will ensure the input is a valid URL

@router.post("/parse_pdf")
async def root(url_input: URLInput):
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
        

        return ''.join(pages_text)
    except:
        raise ValueError('Invalid URL')