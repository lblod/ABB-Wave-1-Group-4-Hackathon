# ABB-Wave-1-Group-4-Hackathon

## Endpoints

On this project, we created two endpoints to perform the whole process:

- `summarize_pdf` endpoint, that fetches a pdf given its url and creates a custom summary of the pdf, following specified rules.
- `process_tasks` fetches every task of the triplestore (pending documents to analyze), and creates several oriented summaries of them. This will run in batch, but could be easily transformed into a scheduler.

## How to run

In order to run the project, run:

```{bash}
> poetry install
> poetry shell
> poetry run fastapi dev app/main.py
```

## Docker deployment

Once configured the `Dockerfile`, run:

- Build the image: `docker buildx build -t pdf_app:latest .`
- Run and expose the container: `> docker run -d -p 0.0.0.0:9090:9090 --name pdf_app_container pdf_app:latest`. The app should be available over [this url](http://hackathon-ai-4.s.redhost.be:9090/docs).