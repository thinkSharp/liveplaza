

Python 3.6 Setup
----------------
 - Download python3.6 tar file and perform linux installation from Google
 - Check the python version (python3 -v)
 - Perform the installation till you see python 3.6 for linux centos
 - Create a virtual environment folder called odoo_dev 
 - Activate the Virtual Environment.
 - Git Clone the odoo-server folder.
 - Git Clone custom folder
 - Go to odoo-server and open odoo.conf file.
 - Paste the text inside the config file

----
```bash
[options]
admin_passwd = Chunny12$akcder
addons_path = /home/ec2-user/odoo_backup/odoo/odoo-server/addons,/home/ec2-user/odoo_backup/odoo/odoo-server/odoo/addons,/home/ec2-user/odoo_backup/odoo/custom/addons,/home/ec2-user/odoo_backup/odoo/custom/themes
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






