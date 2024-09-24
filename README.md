# ABB-Wave-1-Group-4-Hackathon

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