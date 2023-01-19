FROM ubuntu:22.04

WORKDIR /root
SHELL ["/bin/bash", "-ic"]

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN apt update
RUN apt install -y sudo curl wget python3 python3-pip default-jdk git

RUN printf '\
\#!/bin/bash\n\
v=`cat /root/.solc-select/global-version`\n\
/root/.solc-select/artifacts/solc-$v/solc-$v $@\n' > /usr/local/bin/solc
RUN chmod +x /usr/local/bin/solc

RUN groupadd -g "$GROUP_ID" -o docker
RUN useradd -m -u "$USER_ID" -g "$GROUP_ID" -o -s /bin/bash docker && \
    echo "docker:docker" | chpasswd && adduser docker sudo

USER docker
WORKDIR /home/docker

ENV PATH="/home/docker/.local/bin:$PATH"
RUN mkdir 2023-01-blockswap-fv

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash

RUN nvm install 14.16.0
RUN npm install -g yarn
RUN pip3 install certora-cli
RUN pip3 install solc-select
RUN solc-select install 0.8.13

RUN cat - .bashrc <<< force_color_prompt=yes >/tmp/bash && mv /tmp/bash .bashrc
RUN sed -i "s/\(PS1=.*\)@.*:/\1:/g" .bashrc
