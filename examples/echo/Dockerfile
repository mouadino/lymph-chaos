FROM ubuntu

ADD . /repo

WORKDIR repo/

RUN apt-get update
RUN apt-get install --yes python-pip git-core python-dev

RUN pip install git+https://github.com/mouadino/lymph@chaos#egg=lymph
RUN pip install git+https://github.com/mouadino/lymph-chaos@master#egg=lymph-chaos

CMD lymph node --guess-external-ip
