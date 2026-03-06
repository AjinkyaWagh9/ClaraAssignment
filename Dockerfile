FROM n8nio/n8n:1.50.1

USER root

# Install Python3 and pip
RUN (apk add --no-cache python3 py3-pip || /sbin/apk add --no-cache python3 py3-pip)

# Install Python packages needed by the pipeline
RUN pip3 install --break-system-packages \
    gspread \
    google-auth \
    requests

# Make python3 available as python
RUN ln -sf /usr/bin/python3 /usr/bin/python

USER node
