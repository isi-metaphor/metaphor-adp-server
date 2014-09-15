export METAPHOR_DIR=/lfs1/vzaytsev/research/repo/metaphor
export PYTHONPATH=$PYTHONPATH:$METAPHOR_DIR/opt/Metaphor-ADP/pipelines/common
export PYTHONPATH=$PYTHONPATH:$METAPHOR_DIR/opt/Metaphor-ADP/pipelines/Russian
export PYTHONPATH=$PYTHONPATH:$METAPHOR_DIR/opt/Metaphor-ADP/pipelines/English
export PYTHONPATH=$PYTHONPATH:$METAPHOR_DIR/opt/Metaphor-ADP/pipelines/Farsi
export PYTHONPATH=$PYTHONPATH:$METAPHOR_DIR/opt/Metaphor-ADP/pipelines/Spanish

export HENRY_DIR=/opt/adp-install/henry-n700
export BOXER_DIR=/opt/adp-install/boxer
export TMP_DIR=/opt/adp-install/tmp

export GUROBI_HOME=/opt/adp-install/gurobi501/linux64
export GRB_LICENSE_FILE=/opt/adp-install/gurobi.lic.metaphor
export CPLUS_INCLUDE_PATH=/usr/include/python2.7/:/opt/adp-install/gurobi501/linux64/include
export PATH=.:${TEAM_LOCAL}/bin:${TEAM_PUBLIC}/bin:${PATH}:/usr/sbin:/sbin:/usr/bin:${GUROBI_HOME}/bin:${JAVA_HOME}/bin
export LD_LIBRARY_PATH=:${GUROBI_HOME}/lib/:${LD_LIBRARY_PATH}
export LIBRARY_PATH=${GUROBI_HOME}/lib
