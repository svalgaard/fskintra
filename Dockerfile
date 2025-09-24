FROM ubuntu:18.04
LABEL description='https://github.com/svalgaard/fskintra'

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

RUN mkdir -p /fskintra
WORKDIR /fskintra

COPY . /fskintra

RUN apt-get update && \
    apt-get install -y locales python python-pip && \
    localedef -i da_DK -c -f UTF-8 -A /usr/share/locale/locale.alias da_DK

RUN pip install --no-cache-dir -r requirements.txt

VOLUME /root/.skoleintra

ENTRYPOINT ["python", "fskintra.py"]
