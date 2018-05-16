# lcc-service

Check README.pdf for further instructions.

## Installation

This is how to install the entire metaphor pipeline, including the web
service in this repository:

1. Clone repositories for the Metaphor pipeloine and for the Henry
abductive reasoner:
```
mkdir installation-dir
cd installation-dir
git clone https://github.com/isi-metaphor/Metaphor-ADP.git
git clone https://github.com/naoya-i/henry-n700.git
```

2. Compile Henry:
- `cd` to the henry directory and run `make -B`
- You may need to install python-dev, libsqlite3-dev, graphviz and python-lxml

3. Install Boxer:
- Install boxer in a separate subdirectory of installation-dir (called
  boxer maybe).
- First register at: http://svn.ask.it.usyd.edu.au/trac/candc/wiki/Register
- Install Prolog: `sudo apt-get install swi-prolog`
```
svn co http://svn.ask.it.usyd.edu.au/candc/trunk boxer
cd boxer
ln -s Makefile.unix Makefile
make
make bin/boxer
make bin/tokkie
```
- Download the models: http://svn.ask.it.usyd.edu.au/download/candc/models-1.02.tgz
- Uncompress them in the boxer installation directory

4. Install Gurobi: Install gurobi in a separate subdirectory of
installation-dir (called gurobi maybe), and install the license file
somewhere.

5. Clone the web service and set up its directories:

```
git clone https://github.com/isi-metaphor/lcc-service.git

mkdir temp
mkdir temp/lcc-service.tmp
mkdir data
mkdir data/metaphor_kbs
mkdir data/lcc-service
mkdir logs
mkdir logs/lcc-service
```

6. Deploy the web service: The git clone command just downloads the code
but then it needs to be configured and deployed.

- Edit the file `lcc-service/fab/config.{branch_name}.json` depending on if
  you want to install the prod or dev branch of the web service
- For local deployment -- that is, on the same machine:
  - Check the function install in fabfile.py to make sure it runs:
    `basicConfig(branch_name)`, `localConfig()`, `deploy()`
  - Execute `fab install:branch_name`
- For remote deployment -- that is, the deployment directory is on another
  machine to which you have ssh access without password:
  - Edit the ssh username and ssh private key to use (`remoteConfig` function
    in fabfile.py)
  - Make sure you replace `localConfig()` with `remoteConfig()` in the install
    function in fabfile.py
  - Execute `fab install:branch_name`

7. Run:
- Edit the shell.sh script to set the name of the screen session it'll start
  (the -S option)
- Run the shell.sh command
- Within the screen it started, start tempRun.sh
- Disconnect from the screen (CTRL-A D)
