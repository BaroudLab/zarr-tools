FROM python:latest
COPY . .
RUN python -V &&\
    pip install -U pip &&\
    pip install -e .
CMD python -V && /bin/bash
