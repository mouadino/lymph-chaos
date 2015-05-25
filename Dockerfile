FROM ubuntu

ADD examples /services
ADD . /lymph-chaos

WORKDIR lymph-chaos/

RUN apt-get update
RUN apt-get install --yes python-pip git-core python-dev

RUN pip install git+https://github.com/mouadino/lymph@chaos#egg=lymph
RUN pip install /lymph-chaos

ENV PYTHONPATH=/services

CMD lymph node --guess-external-ip
