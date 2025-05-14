FROM python:3.10.4

WORKDIR /src

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    rm requirements.txt

COPY /emomap /src/emomap

CMD ["python", "-m", "emomap.main"]