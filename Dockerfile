FROM ubuntu:latest

RUN cp /etc/apt/sources.list /etc/apt/sources.list.bak
COPY . .
ADD sources.list /etc/apt/ 

RUN apt-get update
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