FROM python:2-slim
MAINTAINER askeolsson@gmail.dk

RUN mkdir -p /fskintra
WORKDIR /fskintra

COPY requirements.txt /fskintra
#RUN apk add --update \
#    build-base \
#    libxml2-dev \
#    libxslt-dev \
#    && rm -rf /var/cache/apk/*

RUN  apt-get update && \
             apt-get install -y build-essential locales && \
             pip install --no-cache-dir -r requirements.txt && \
             localedef -i da_DK -c -f UTF-8 -A /usr/share/locale/locale.alias da_DK && \
             apt-get remove -y --purge build-essential && \
             apt-get clean && \
            rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . /fskintra

VOLUME /root/.skoleintra

ENTRYPOINT ["python", "fskintra.py"]