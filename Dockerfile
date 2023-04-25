FROM continuumio/anaconda3:latest

ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /workspace

COPY environment.yml /workspace/
# RUN export https_proxy=http://127.0.0.1:7890;export http_proxy=http://127.0.0.1:7890;export all_proxy=socks5://127.0.0.1:7890
RUN conda update -n base -c defaults conda 
RUN conda env update -f environment.yml 
RUN conda clean --all --yes 

CMD ["bash"]
