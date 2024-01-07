FROM circleci/python:2

COPY ./bin /home/circleci/bin

RUN bash ~/bin/install_deps.sh

COPY . /home/circleci/repo

WORKDIR /home/circleci/repo

RUN echo "PS1=\"\\\\n____[\\u@\\h] [\\w]____\\\\n $ \"" >> ~/.bashrc

CMD bash

