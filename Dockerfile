FROM selenium/standalone-chrome:131.0
WORKDIR /app
ENV .env=/app
COPY . /app
RUN sudo pip install -r requirements.txt --break-system-packages
CMD ["python3","main.py"]
