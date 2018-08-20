FROM debian:8.10

MAINTAINER Jonathan Gordon <jgordon@isi.edu>

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8


# Install basic system dependencies.

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -q -y --fix-missing && \
    apt-get install -q -y --fix-missing --no-install-recommends \
        bzip2 ca-certificates g++ git-core graphviz libsqlite3-dev make \
        openjdk-7-jre python-dev python-lxml python-nltk swi-prolog wget

RUN apt-get clean -q


# Install Gurobi.

ENV GUROBI_INSTALL /research/ext/gurobi
ENV GUROBI_HOME $GUROBI_INSTALL/linux64

RUN mkdir -p $GUROBI_INSTALL && \
    wget http://packages.gurobi.com/5.6/gurobi5.6.3_linux64.tar.gz && \
    tar xvzf gurobi5.6.3_linux64.tar.gz && \
    mv gurobi563/linux64 $GUROBI_INSTALL && \
    mkdir $GUROBI_HOME/scripts && \
    rm -rf $GUROBI_HOME/docs && \
    rm -rf $GUROBI_HOME/examples && \
    rm -rf $GUROBI_HOME/src && \
    rm -rf gurobi563 && \
    rm -f gurobi5.6.3_linux64.tar.gz

ENV PATH $PATH:$GUROBI_HOME/bin
ENV CPLUS_INCLUDE_PATH $GUROBI_HOME/include:$CPLUS_INCLUDE_PATH
ENV LD_LIBRARY_PATH $GUROBI_HOME/lib:$LD_LIBRARY_PATH
ENV LIBRARY_PATH $GUROBI_HOME/lib:$LIBRARY_PATH
ENV GRB_LICENSE_FILE $GUROBI_INSTALL/license/gurobi.lic


# Install Henry.

WORKDIR /research/repo
RUN git clone https://github.com/isi-metaphor/henry-n700.git henry

WORKDIR /research/repo/henry
RUN make -B

ENV HENRY_DIR=/research/repo/henry


# Install Boxer.

WORKDIR /research/ext

RUN git clone https://github.com/jgordon/boxer

WORKDIR /research/ext/boxer

RUN make && \
    make bin/boxer && \
    make bin/tokkie

RUN tar xvjf models-1.02.tar.bz2 && \
    rm models-1.02.tar.bz2

ENV BOXER_DIR=/research/ext/boxer


# Install Metaphor-ADP.

WORKDIR /research/repo
RUN git clone https://github.com/isi-metaphor/metaphor-adp.git metaphor

# WORKDIR /research/repo/metaphor
# RUN git checkout develop
# RUN git pull

ENV METAPHOR_DIR=/research/repo/metaphor
ENV PYTHONPATH=$PYTHONPATH:$METAPHOR_DIR/pipelines/common
ENV PYTHONPATH=$PYTHONPATH:$METAPHOR_DIR/pipelines/English
ENV PYTHONPATH=$PYTOHNPATH:$METAPHOR_DIR/pipelines/Spanish
ENV PYTHONPATH=$PYTHONPATH:$METAPHOR_DIR/pipelines/Farsi
ENV PYTHONPATH=$PYTHONPATH:$METAPHOR_DIR/pipelines/Russian


# Install lcc-service.

RUN apt-get install -q -y --fix-missing --no-install-recommends \
        fabric python-django python-jinja2 python-git python-lz4 \
        python-pexpect python-pip python-regex python-simplejson

RUN pip install sexpdata

COPY . /research/repo/lcc-service

#

RUN mkdir -p /research/temp/uploads
ENV TMP_DIR=/research/temp
RUN mkdir -p /research/logs/lcc-service
RUN mkdir -p /research/data/lcc-service


#

WORKDIR /research/repo/lcc-service

ENV DJANGO_SETTINGS_MODULE=lccsrv.settings

RUN ./manage.py syncdb --noinput

RUN python2.7 -c "from django.contrib.auth.models import User; User.objects.create_superuser('metaphor', '', 'metaphor')"

CMD ["./manage.py", "runserver", "0.0.0.0:8000"]
