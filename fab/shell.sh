
#!/bin/bash
screen env -i HOME=$HOME TERM=$TERM bash --init-file ./bashrc.sh -S {{STAGE}}_{{NGINX_PORT}}
