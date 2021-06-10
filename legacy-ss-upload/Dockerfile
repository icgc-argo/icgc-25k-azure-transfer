FROM ghcr.io/overture-stack/score:5.3.0

LABEL org.opencontainers.image.source https://github.com/icgc-argo/icgc-25k-azure-transfer

ENV PATH="/tools:${PATH}"

COPY *.py /tools/

ENTRYPOINT ["/usr/bin/env"]

CMD ["/bin/bash"]
