FROM python:3.12.2
WORKDIR /app
ADD app/ .
RUN pip install -r requirements.txt 
EXPOSE 8501
CMD ["streamlit", "run", "Home.py"]