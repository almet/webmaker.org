make.mozilla.org
================

This app is built using Mozilla's Playdoh.

Deployment instructions are towards the bottom of this file.

Local development
=================

We're using PostGIS + GeoDjango for the DB, so you'll also need the following installed

* Postgresql 8.4 +
* PostGIS >= 1.4 && < 2.0
* Geos
* Proj4
* GDAL

Checkout the sourcecode and init the git submodules:

    git clone --recursive git://github.com/mozilla/webmaker.org

If at any point you realize you forgot to clone with the recursive flag, you
can fix that by running:

    git submodule update --init --recursive


Mac OS X
--------

With [Homebrew][brew], installing PostGIS and GDAL will install all you need:

    brew update
    brew install postgis gdal

[brew]: http://mxcl.github.com/homebrew/

Ubuntu
------

For Ubuntu 10.04, see the information in our Puppet config (`./puppet/manifests/dev.pp` and the classes in `./puppet/manifests/classes`)

For Ubuntu release >= 11.10, this should work:

    sudo apt-get install binutils gdal-bin libproj-dev postgresql-9.1-postgis \
         postgresql-server-dev-9.1

Once those are installed, then `pip install -r requirements/compiled.txt` should 
work as expected.

GeoDjango
---------

GeoDjango is installed as part of Django. You need to take a look at the installation 
instructions at [https://docs.djangoproject.com/en/1.3/ref/contrib/gis/install/#post-installation] 
to get PostGIS configured properly with Django. Ubuntu's version ships with a postgis-template generation script, which you can see used in `./puppet/manifests/classes/postgis.pp`

Making it run locally
=====================

Once you have all the dependencies installed, you need to create a settings
file.

    cp make_mozilla/settings/local.py{-dist,}

And then edit the settings file to match your needs, here is the section about
the databases:

    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'webmaker',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'localhost',
            'PORT': '5432',
            'TEST_CHARSET': 'utf8',
            'TEST_COLLATION': 'utf8_general_ci',
        },
    }


Setting up the database
-----------------------

Once you've installed postgis, you need to create a template for it, and then
create your database with this template. For postgis 1.5:

    cd /tmp && wget https://raw.github.com/django/django/master/docs/ref/contrib/gis/install/create_template_postgis-1.5.sh
    sudo su postgres
    /tmp/create_template_postgis-1.5.sh

And finally create the database:

    createdb -T template_postgis webmaker

Populating it
-------------

    ./manage.py syncdb
    ./manage.py migrate
    

Compiling the assets
--------------------

You also need to compile the assets, be sure to update your settings with the path to your LESS executable:

    LESS_BIN = "/usr/local/bin/lessc"

And then run:

    ./manage.py compress_assets

Deployment
==========

We're making heavy use of [Fabric][fab] and [Puppet][] to automate deployment. Deployment has been tested on a Ubuntu 10.04 box, and puppet recipes will likely fail on later versions of Ubuntu (or any Debian version), and certainly would on RHEL / CentOS systems.

[fab]: http://docs.fabfile.org/
[Puppet]: http://puppetlabs.com/

Note that we're using Puppet 0.25, because that's what comes with Ubuntu 10.04. It's old, you'll find a lot of newer recipes and examples out on the web won't run unmodified on it.

Prequisites
-----------

* A machine set up for local development

* A user with `sudo` access on a Ubuntu 10.04 box with `openssh-server` installed and running. No other pre-puppet dependencies.

* The machine you want to deploy to listed in the hosts dict in `fabfile.py`
* The SSH pubkey of any developers who should have deploy access contained in `puppet/files/deploy_keys` (this will become the `.ssh/authorized_keys` file for the server user the app runs as.

Initial setup
-------------

```bash
fab puppet.setup
fab puppet.apply
fab deploy.cold
```

`fab puppet.setup` installs the Puppet packages on the box.
`fab puppet.apply` uploads and applies the current puppet recipes. Note that this is not done from Git, but from the deployers working directory, so be careful about uncommitted changes.
`fab deploy.cold` Actually deploys the app, performing first-run setup and running DB migrations.

If you're not deploying to the default server (you can change the default on line 21 of `fabfile.py`) then you need to specify which set of hosts to use:

```
TO=production fab puppet.setup
TO=production fab puppet.apply
TO=production fab deploy.cold
```

If your sudoer's username on the box you're deploying too doesn't match your local username:

```
fab -u remote_username puppet.setup
```

If you need to do both the above mods:

```
TO=production fab -u remote_username puppet.setup
```

Updates to Puppet
----------------

```bash
fab puppet.apply
```

Provided there are no bugs in the puppet recipes, running `fab puppet.apply` should only do something if there's a change to apply - it's safe to run multiple times, and even if there are no new changes.

Regular deployment
------------------

````bash
fab deploy
```

This doesn't run the Migrations. To deploy and run migrations run:

```bash
fab deploy_with_migrations
```

Notes on the Puppet setup
-------------------------

The main Puppet manifest is `puppet/manifests/dev.pp`, which in turn includes all the rest of the resources in a single class, then includes that class - puppet then tries to make sure all the resources described in `puppet/manifests/classes/*.pp` are included and brought up to date. If you need to add more things to the Puppet recipes, add them in a file in `puppet/manifests/classes` and then put an include line into `puppet/manifests/dev.pp`

E.g., add resources to `puppet/manifests/classes/my_file.pp` and then, in `dev.pp`:

```
class dev {
  include app_users
  ...
  include my_file
}
```

I don't think this is an entirely standard way of doing things, but it works well with a single-machine single-OS deployment.

playdoh: about the framework
============================

Mozilla's Playdoh is a web application template based on [Django][django].

Patches are welcome! Feel free to fork and contribute to this project on
[github][gh-playdoh].

Full Playdoh [documentation][docs] is available as well.

[django]: http://www.djangoproject.com/
[gh-playdoh]: https://github.com/mozilla/playdoh
[docs]: http://playdoh.rtfd.org/


License
-------
This software is licensed under the [New BSD License][BSD]. For more
information, read the file ``LICENSE``.

[BSD]: http://creativecommons.org/licenses/BSD/

