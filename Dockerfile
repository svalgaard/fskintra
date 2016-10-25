FROM python:2-onbuild

ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["python", "fskintra.py"]
