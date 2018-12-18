# Molgenis Commander [BETA]

### Installing

In a terminal, run:

```
pip install molgenis-commander
```

### Development
Want to help out? Fork and clone this repository, go to the root of the project and create a virtual environment:

```
python -m virtualenv env
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
