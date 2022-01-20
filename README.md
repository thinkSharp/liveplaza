
GitHub Desktop Setup
----------------

 - Download Github Desktop for the local box.
 - Once downloaded Click File > Clone Repository > URL.
 - Add the following link in the URL text box.
 ```bash 
 https://github.com/thinkSharp/liveplaza
 ```
 - Once done add the local path as well.
 - Now Click Clone.
 - Now select the repository liveplaza, branch dev.
 - Click create new branch. 
 - Add the name (Your Name) for the branch and choose dev branch.
 

Python 3.6 Setup (Command Line Setup)
----------------
 - Download python3.6 tar file and perform linux installation from Google
 - Check the python version (python3 -v)
 - Perform the installation till you see python 3.6 for linux centos.
 - Create a virtual environment folder called odoo_dev.
 - Locate the bin folder
 - Activate the Virtual Environment.
 
 ```bash
source bin/activate

```

 - If using IDE like Eclipse or Pycharm kindly make use of Python 3.6 virtual Environment and skip to the LivePlaza local setup.
 

LivePlaza Local setup
---------------- 

 - Git Clone the liveplaza folder.
 - Go to Folder odoo-server and open odoo.conf file.
 - Paste the text inside the config file

----
```bash
[options]
admin_passwd = Chunny12$akcder
addons_path = ~/odoo-server/addons,~/odoo-server/odoo/addons,~/custom/addons,~/custom/themes
db_host = localhost
db_port = 5432
db_user = odoo
db_password = Chunny12$akcder
http_port = 5001
xmlrpc_port = 5001
workers = 5
max_cron_threads = 2

```

----
 - Install the requirements.txt file 

```bash
python3 -m pip install -r requirements.txt
```


 - Run the odoo-bin from the odoo-server with the configuration file and the database name



```bash
python3 odoo-bin -c odoo.conf (to start the odoo- server)

```






PostgreSQL Setup
----------------
 - Install postgres 10 locally
 - Create or Add user “odoo” as super user.
 - Login into the psql command prompt.


```bash
sudo -u postgres psql
```

 - Create a Database named livep and alter the permissions.

```bash
CREATE DATABASE livep; 

ALTER DATABASE livep OWNER TO odoo;

```


 - Once created verify the database with the owner name.

```bash
\l 
```

 - Dump all the data from the dump.sql file into the livep database.
 

```bash

sudo -u postgres psql livep < dump.sql

```

GitHub Creating Pull Request
----------------
 - Once modifying code to the branch commit, push all the changes to your branch.
 - Once completing the click create Pull Request.
 - Once redirected to thr web page on your browser click merge to dev branch.
 - Add reviewer and add Vishal.
 - Add comments and click create PR.


-test



