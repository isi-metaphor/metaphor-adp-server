lcc-service
===========
checkout the README.pdf file for further instructions.
<br/>Installation of the entire Metaphor pipeline including the web service (this repo).

```
mkdir installation-dir
cd installation-dir
git clone https://github.com/isi-metaphor/Metaphor-ADP.git
git clone https://github.com/naoya-i/henry-n700.git
>> cd in the henry directory and run "make -B"
>> you may need to install python-dev, libsqlite3-dev, graphviz and python-lxml

install boxer in a separate subdirectory of installation-dir (called boxer maybe)
>> first register at: http://svn.ask.it.usyd.edu.au/trac/candc/wiki/Register
>> svn co http://svn.ask.it.usyd.edu.au/candc/trunk boxer
>> cd boxer
>> ln -s Makefile.unix Makefile
>> make
>> make bin/boxer (you need "sudo apt-get install swi-prolog" for this step)
>> make bin/tokkie
>> download the models: http://svn.ask.it.usyd.edu.au/download/candc/models-1.02.tgz
>> uncompress them in the boxer installation directory

install gurobi in a separate subdirectory of installation-dir (called gurobi maybe), install the license file also somewhere

git clone https://github.com/isi-metaphor/lcc-service.git

mkdir temp
mkdir temp/lcc-service.tmp
mkdir data
mkdir data/metaphor_kbs
mkdir data/lcc-service
mkdir logs
mkdir logs/lcc-service

> now let's deploy the web service. The git clone command just downloads the code but then it neewd to be configured and deployed.
edit the file lcc-service/fab/config.{branch_name}.json dependig if you want to install the prod or dev branch of the web service
- for local deployment, that is, on the same machine.
 - check the function install in fabfile.py to make sure it runs: basicConfig(branch_name), localConfig(), deploy()
 - execute fab install:branch_name
- for remote deployment, that is, the deployment directory is on another machine to which you have ssh access without password.
 - edit the ssh username and ssh private key to use (remoteConfig function in fabfile.py)
 - make sure you replace localConfig() with remoteConfig() in the install function in fabfile.py
 - execute fab install:branch_name
```
to run:
- edit the shell.sh script to set the name of the screen session it'll start (-S option)
- run the shell.sh command
- within the screen it started, start tempRun.sh
- deconnect from the screen (CTRL-A D)

done
