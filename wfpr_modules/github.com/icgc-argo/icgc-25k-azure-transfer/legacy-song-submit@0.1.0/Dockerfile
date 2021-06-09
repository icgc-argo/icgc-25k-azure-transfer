FROM python:3.7.5-slim-buster

LABEL org.opencontainers.image.source https://github.com/icgc-argo/icgc-25k-azure-transfer

RUN pip install --upgrade pip && \
    pip install requests

ENV PATH="/tools:${PATH}"

COPY *.py /tools/

RUN groupadd -g 1000 ubuntu && \
    useradd -l -u 1000 -g ubuntu ubuntu && \
    install -d -m 0755 -o ubuntu -g ubuntu /home/ubuntu

USER ubuntu

ENTRYPOINT ["/usr/bin/env"]

CMD ["/bin/bash"]
