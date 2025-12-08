FROM runpod/base:0.4.0-cuda11.8.0

# System deps
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Handler
COPY handler.py /handler.py

CMD ["python", "-u", "/handler.py"]


