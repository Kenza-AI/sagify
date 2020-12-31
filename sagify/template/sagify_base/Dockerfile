ARG python_version
FROM python:$python_version-slim-stretch

LABEL maintainer="Kenza AI <support@kenza.ai>"

RUN apt-get -y update && apt-get install -y --no-install-recommends \
         make \
         nginx \
         ca-certificates \
         g++ \
         git \
    && rm -rf /var/lib/apt/lists/*

# PYTHONUNBUFFERED keeps Python from buffering the standard
# output stream, which means that logs can be delivered to the user quickly. 
# PYTHONDONTWRITEBYTECODE keeps Python from writing the .pyc files which are unnecessary in this case. 

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

ARG requirements_file_path
ARG module_path
ARG target_dir_name

COPY ${requirements_file_path} /opt/program/sagify-requirements.txt
WORKDIR /opt/program/${target_dir_name}

# Here we get all python packages.
RUN pip install flask gevent gunicorn future
RUN pip install -r ../sagify-requirements.txt && rm -rf /root/.cache
RUN apt-get -y purge --auto-remove git

COPY ${module_path} /opt/program/${target_dir_name}

ENTRYPOINT ["sagify_base/executor.sh"]
