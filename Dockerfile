FROM continuumio/miniconda

EXPOSE 8000

WORKDIR .

COPY . .

RUN conda env update --file environment.yml

CMD ["python", "flask_app.py" ]
