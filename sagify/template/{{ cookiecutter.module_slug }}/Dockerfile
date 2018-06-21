# Build an image that can do training and inference in SageMaker
# This is an image that uses the nginx, gunicorn, flask stack
# for serving inferences in a stable way.

FROM python:{{ cookiecutter.python_version }}-slim-stretch

MAINTAINER Amazon AI <support@kenza.ai>


RUN apt-get -y update && apt-get install -y --no-install-recommends \
         nginx \
         ca-certificates \
         g++ \
    && rm -rf /var/lib/apt/lists/*

# Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the train and serve programs are found when the container is invoked.

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

ARG requirements_file_path
ARG module_path
ARG target_dir_name

COPY ${requirements_file_path} /opt/program/sagify-requirements.txt
COPY ${module_path} /opt/program/${target_dir_name}
WORKDIR /opt/program/${target_dir_name}

# Here we get all python packages.
RUN pip install flask gevent gunicorn future
RUN pip install -r ../sagify-requirements.txt && rm -rf /root/.cache

ENTRYPOINT ["sagify/executor.sh"]
