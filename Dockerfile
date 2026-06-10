FROM python:3.10-slim

# Set up a generic, secure user to comply with Hugging Face requirements
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy and install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of the web app code
COPY --chown=user . .

# Expose the mandatory port required by Hugging Face Spaces
EXPOSE 7860

# Launch Streamlit pointing to the correct address configuration
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
