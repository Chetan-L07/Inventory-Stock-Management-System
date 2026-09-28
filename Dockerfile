FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose Streamlit default port (7860 for Hugging Face Spaces, 8501 for generic)
EXPOSE 7860
EXPOSE 8501

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
