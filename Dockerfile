FROM python:2
LABEL description='https://github.com/svalgaard/fskintra'

ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING UTF-8

RUN mkdir -p /fskintra
WORKDIR /fskintra

COPY . /fskintra

RUN apt-get update && \
    apt-get install -y locales && \
    localedef -i da_DK -c -f UTF-8 -A /usr/share/locale/locale.alias da_DK && \
    apt-get clean && \
    sed -i 's/DEFAULT@SECLEVEL=2/DEFAULT@SECLEVEL=1/g' /etc/ssl/openssl.cnf && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

VOLUME /root/.skoleintra

ENTRYPOINT ["python", "fskintra.py"]
