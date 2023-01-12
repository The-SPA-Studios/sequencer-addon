# Contribution Guidelines

## Setup Developer Environment
This is a step-by-step guide to get a functional development environment for maintaining Blender Python add-ons, using Visual Studio Code IDE.

### Requirements
Download and install for your platform:
- [Blender 3.3 LTS](https://blender.org/download) - use local development build or use a portable zip version
- [VSCode](https://code.visualstudio.com/)
- [Git](https://git-scm.com/downloads)

### Create a Python Virtual Environment
Python virtual environments are useful to create isolated development environments, especially regarding package management.

- define the folder where you will be storing your virtual environments (here: `/path/to/venvs`)
- create a virtual environment for Blender development using Blender's embedded Python interpreter
  - location: `{blender_install_path}/{blender_version}/python/bin/python`
  - referred to as BL_PYEXE in the rest of this document

```
cd /path/to/venvs
# Make sure pip is available
BL_PYEXE -m ensurepip
# Create a new virtual environment
BL_PYEXE -m venv blender_dev
cd blender_dev
# Windows:
Script\activate
# Linux:
source Script/activate
```
Now that the virtual environment is activated, install the requirements
```
pip install -r requirements.dev.txt
```

### Setting up VSCode
Open VSCode.

#### Configure Python
- make sure the Python langage extension is enabled - open any `.py` file to trigger its installation.
- in the settings, setup the path to your virtual envs folder (either in UI or in JSON):
- WARNING:  use the path to the folder **containing** `blender_dev`
```
"python.venvPath": "/path/to/venvs"
```
- restart VSCode to update the list of available interpreters

Now, open a project - i.e the folder containing the source of an add-on.
- open a Python file to trigger the Python interpreter selection
- interpreter: click on "Select the Python Interpreter" and set it to `blender_dev`
- linter: Ctrl+Shift+P > Select Linter > flake8


#### Blender Development extension
From the Extensions panel, install `Blender Development` by Jacques Lucke.

New commands are available in the Command Palette (Ctrl+Shift+P): 
- **Blender: Start**
    - chose a Blender executable the first time
        - requires Admin privileges if Blender is installed in a protected folder
    - this automatically installs the addon in development
    - Python debugger is attached to the instance of Blender, enabling the use of breakpoints in Python code
- **Blender: Reload Addons**
    - reload the addon in development
    - for more convenience, you can activate the reloadOnSave option in the extension settings
      - `"blender.addon.reloadOnSave": true`

#### Other Recommanded Extensions
- Version Control
  - Git Graph
  - GitLens
  - Gitlab
- Utilities
  - Clipboard Manager


## Analysis and Testing

Running static analysis and unit tests requires a complete Blender Python environment with core packages (bpy, mathutils...) available.
First, install requirements within Blender's own interpreter.
```
BL_PYEXE -m pip install -r requirements.tests.py
```

### Running static analysis
```
blender -b -P scripts\run_mypy.py
```

### Running unit tests

```
blender -b -P scripts\run_pytest.py
```


## API Documentation
The API documentation is generated automatically from Python docstrings using sphinx.  
Like for analysing and testing, this requires a complete Blender Python environment.

First, install the requirements in Blender's own interpreter.
```
BL_PYEXE -m pip install -r requirements.apidoc.txt
```

Now, using the Blender executable from this installation, run

```
blender -b -P scripts\run_sphinx-build.py
```

This generates a static HTML site, within the `apidoc/generated/build` folder by default.
