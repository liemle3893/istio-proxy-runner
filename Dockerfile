FROM python:3.5-jessie  AS build-env
ADD . /app
WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip install -r ./requirements.txt

FROM gcr.io/distroless/python3
COPY --from=build-env /app /app
COPY --from=build-env /usr/local/lib/python3.5/site-packages /usr/local/lib/python3.5/site-packages

WORKDIR /app
ENV PYTHONPATH=/usr/local/lib/python3.5/site-packages

VOLUME ["/tmp/run/docker.sock"]

ENV DOCKER_BASE_URL="unix://tmp/run/docker.sock"
ENV CLUSTER_NAME=""
ENV BASE_IMAGE_NAME=""
ENV BASE_IMAGE_SUFFIX=""

CMD ["main.py"]
