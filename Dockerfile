FROM ubuntu:latest

RUN apt-get update --fix-missing 
RUN apt-get install -y git cmake g++ nvidia-cuda-toolkit

WORKDIR /fastllm
COPY . /fastllm
RUN mkdir build
WORKDIR /fastllm/build
RUN cmake .. -DUSE_CUDA=ON
RUN make -j
WORKDIR /fastllm/build/tools
RUN python setup.py install
WORKDIR /fastllm/build/tools  
RUN python setup.py install
WORKDIR /fastllm/build
RUN ./webui -p model.flm --port 1234