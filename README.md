lcc-service
===========
checkout the README.pdf file for further instructions.
<br/>Installation of the entire Metaphor pipeline including the web service (this repo).

```
mkdir installation-dir
cd installation-dir
git clone https://github.com/isi-metaphor/Metaphor-ADP.git
git clone https://github.com/naoya-i/henry-n700.git
> install boxer in a separate subdirectory of installation-dir (called boxer maybe)
> install gurobi in a separate subdirectory of installation-dir (called gurobi maybe), install the license file also somewhere
git clone https://github.com/isi-metaphor/lcc-service.git
mkdir temp
mkdir temp/lcc-service.dev.tmp
mkdir data
mkdir data/metaphor_kbs
mkdir data/lcc-service
mkdir logs
mkdir logs/lcc-service.dev

> now let's deploy the web service. The git clone command just downloads the code but then it neewd to be configured and deployed.
edit the file lcc-service/fab/config.{dev,prod}.json dependig if you want to install the prod or dev branch of the web service
- for local deployment, that is, on the same machine.
 - check the function devdeploy/proddeploy in fabfile.py to make sure it runs: dev()/prod(), local(), init() and deploy()
 - execute fab devdeploy
- for remote deployment, that is, the deployment directory is on another machine to which you have ssh access without password.
 - edit the ssh username and ssh private key to use.
 - make sure you replace local() with deploy() in you devdeploy or proddeploy function.
```
to run:
- edit the shell.sh script to set the name of the screen session it'll start (-S option)
- run the shell.sh command
- within the screen it started, start tempRun.sh
- deconnect from the screen (CTRL-A D)

done
