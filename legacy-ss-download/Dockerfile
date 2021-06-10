FROM ghcr.io/overture-stack/score:5.3.0

LABEL org.opencontainers.image.source https://github.com/icgc-argo/icgc-25k-azure-transfer

RUN apt update -y && \
    apt install -y python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip && \
    pip install requests

ENV PATH="/score-client/bin:/tools:${PATH}"

COPY *.py /tools/

RUN groupadd -g 2000 ubuntu && \
    useradd -l -u 2000 -g ubuntu ubuntu && \
    install -d -m 0755 -o ubuntu -g ubuntu /home/ubuntu

USER ubuntu

ENTRYPOINT ["/usr/bin/env"]

CMD ["/bin/bash"]
