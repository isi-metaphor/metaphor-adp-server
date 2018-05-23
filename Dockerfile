FROM debian:8.10

MAINTAINER Jonathan Gordon <jgordon@isi.edu>

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8


# Install basic system dependencies.

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -q -y --fix-missing && \
    apt-get install -q -y --fix-missing --no-install-recommends \
        bzip2 ca-certificates g++ git-core graphviz libsqlite3-dev make \
        python-dev python-lxml python-nltk swi-prolog wget

RUN apt-get clean -q


# Install Gurobi.

ENV GUROBI_INSTALL /research/ext/gurobi
ENV GUROBI_HOME $GUROBI_INSTALL/linux64
ENV PATH $PATH:$GUROBI_HOME/bin
ENV CPLUS_INCLUDE_PATH $GUROBI_HOME/include:$CPLUS_INCLUDE_PATH
ENV LD_LIBRARY_PATH $GUROBI_HOME/lib:$LD_LIBRARY_PATH
ENV LIBRARY_PATH $GUROBI_HOME/lib:$LIBRARY_PATH
ENV GRB_LICENSE_FILE $GUROBI_INSTALL/license/gurobi.lic

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


# Install Henry.

WORKDIR /research/repo
RUN git clone https://github.com/isi-metaphor/henry-n700.git henry

WORKDIR /research/repo/henry
RUN make -B


# Install Boxer.

WORKDIR /research/ext

RUN git clone https://github.com/jgordon/boxer

RUN cd boxer && \
    make && \
    make bin/boxer && \
    make bin/tokkie

RUN cd boxer && \
    tar xvjf models-1.02.tar.bz2 && \
    rm models-1.02.tar.bz2


# Install Metaphor-ADP.

WORKDIR /research/repo
RUN git clone https://github.com/isi-metaphor/Metaphor-ADP.git metaphor


# Install lcc-service.

RUN apt-get install -q -y --fix-missing --no-install-recommends \
        fabric openjdk-7-jre python-django python-jinja2 python-git \
        python-lz4 python-pexpect python-pip python-regex python-simplejson \
        screen

RUN pip install sexpdata

COPY . /research/repo/lcc-service

#

RUN mkdir -p /research/temp/uploads
RUN mkdir -p /research/logs/lcc-service
RUN mkdir -p /research/data/lcc-service
RUN mkdir /research/data/kbs

#

WORKDIR /research/repo/lcc-service

ENV DJANGO_SETTINGS_MODULE=lccsrv.settings

RUN ./manage.py syncdb --noinput

RUN python -c "from django.contrib.auth.models import User; User.objects.create_superuser('metaphor', '', 'metaphor')"

CMD ["./manage.py", "runserver", "0.0.0.0:8000"]
