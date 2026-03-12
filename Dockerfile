FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app
COPY . .
RUN pip install playwright python-dotenv
RUN playwright install chromium
RUN mkdir -p /app/screenshots

CMD ["python", "reserva_final.py"]