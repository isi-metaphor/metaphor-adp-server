
#!/bin/bash
screen -S {{STAGE}}_{{NGINX_PORT}} env -i HOME=$HOME TERM=$TERM bash --init-file ./bashrc.sh 
