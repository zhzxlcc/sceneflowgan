FROM nvidia/cuda:9.0-base-ubuntu16.04

## Python
# Pick up some TF dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
       build-essential \
       gfortran \
       libsndfile1 \
       libatlas-dev \
       liblapack-dev \
       libffi-dev \
       cmake \
       cuda-command-line-tools-9-0 \
       cuda-cublas-9-0 \
       cuda-cufft-9-0 \
       cuda-curand-9-0 \
       cuda-cusolver-9-0 \
       cuda-cusparse-9-0 \
       libcudnn7=7.0.3.11-1+cuda9.0 \
       libnccl2=2.2.13-1+cuda9.0 \
       libfreetype6-dev \
       libhdf5-serial-dev \
       libpng12-dev \
       libsm6 \
       libzmq3-dev \
       pkg-config \
       python3-tk \
       software-properties-common \
       unzip \
       vim \
       && \
   apt-get clean && \
   rm -rf /var/lib/apt/lists/*

ARG USE_PYTHON_2_NOT_3=True
ARG PYTHON=python
ARG PIP=pip$

RUN apt-get update && apt-get install -y \
   ${PYTHON} \
   ${PYTHON}-pip

RUN ${PIP} install --upgrade \
   pip \
   setuptools

RUN ${PIP} install \
        matplotlib \
        tensorflow-gpu\
        scipy \
        numpy \
        h5py==2.9.0 \
        keras==2.2.4 \
        numpy==1.16.4 \
        pypng==0.0.19 \
        tqdm 
        

RUN apt-get install -y htpdate

RUN apt-get install -y sudo

CMD ["bash"]
