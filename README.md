[![Quality Status](https://sonarcloud.io/api/project_badges/measure?project=org.molgenis%3Acommander&metric=alert_status)](https://sonarcloud.io/dashboard?id=org.molgenis%3Acommander)

# MOLGENIS Commander

MOLGENIS Commander makes managing your [MOLGENIS application](https://molgenis.github.io//) a breeze! It offers a rich set of commands for oft-repeated actions
like importing datasets and managing groups and users. Besides catering to the data oriented user it also aims to provide 
an extensive toolkit for developers working on MOLGENIS.

Want to get started right away? Read [Getting started](https://github.com/molgenis/molgenis-tools-commander/wiki/Getting-started) 
on the wiki!

### Teaser

Easily add groups and users and configure their roles:

[![asciicast](https://asciinema.org/a/297760.svg)](https://asciinema.org/a/297760)

Import datasets with a single command:

[![asciicast](https://asciinema.org/a/297766.svg)](https://asciinema.org/a/297766)

Tie it all together by creating a script:

[![asciicast](https://asciinema.org/a/297763.svg)](https://asciinema.org/a/297763)

For a full list of features, go:

```
mcmd --help
```

### How to install
You can install the Commander using `pip`. For more information and troubleshooting tips, see the [Installation guide](https://github.com/molgenis/molgenis-tools-commander/wiki/Installation-guide)


### Scripts

It's possible to collect multiple commands in a script. Please read the [Scripts documentation](https://github.com/molgenis/molgenis-tools-commander/wiki/Scripts) for more information.


### Development
Want to help out? Fork and clone this repository, go to the root of the project and create a virtual environment:

```
python -m venv env
```

Now activate the environment. How to do this depends on your operating system, read 
[the virtualenv docs](https://virtualenv.pypa.io/en/latest/userguide) for more info. 
The following example assumes MacOS:


```
source env/bin/activate
```

Then install the project in development mode:
```
pip install -e .
```

The `mcmd` command will now be available in this virtual environment! If you want to
leave the environment, use `deactivate`.

### Running tests
The project contains unit- and integration tests. 

#### Running tests from the command line
To run all the unit tests from the command line, go:

```
python setup.py test --addopts "-m unit --ignore=tests/integration/" 
```

The integration tests require a running MOLGENIS application to test against. They can be run like this:
 
```
python setup.py test --addopts "-m integration --ignore=tests/unit/"
```
 
By default the localhost is chosen (username: admin, password: admin), but it's possible to configure a different server:

```
python setup.py test --addopts "-m integration --ignore=tests/unit/ --url=<your_url> --username=<admins username> --password=<admins password>" 
```

#### Running tests in PyCharm
To run the tests in PyCharm, first set the default test runner to 'pytest'. 

![Configure default test runner](docs/default_test_runner.png)

Then create pytest run configurations, by going to `Edit Configurations -> + -> Python tests -> pytest` and using
the same arguments as above:

![Setting up run configuration](docs/run_configuration.png)


