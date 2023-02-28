# What is XellGrid

XellGrid is a Jupyter based grid application that provides intuitive, powerful and fast data analysis and computationa functionalities for developers, data scientists, business analysts, and data analysts. It is compatible with multiple data table structures including Pandas, PyArrow, Dask, etc. 
 
# Main Features 
- Leverage computational power of Python ecosystems and supports both advanced Python scripting and "low code/no code" practices   
- Close integration with Pandas, one of the most popular Python data analysis packages 
- "Excel" like user interfaces, supports multiple tabs and commonly used features like vlookup, pivot, etc.  
- Built-in high performance computation engine and support super size (100G+) data analysis and manipulation 
- Supports both cloud based and local resource based computation, significatly reduce cloud computation cost    
- Support smart data analysis scripting based on latest NLP advancements.

## Install
---------
- ` git clone https://github.com/xellgrid/XellGrid`


## Requirements

* JupyterLab >= 3.0

## Install

To install the extension, execute:

```bash
pip install xellgrid
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall xellgrid
```

## Running from source & testing your changes

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the xellgrid directory
# Install package in development mode
python -m venv env && . env/bin/activate  # for linux environment
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite

# Install frontend dependencies
jlpm install
# Build extension Typescript source after making changes
jlpm run build
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm run watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm run build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
pip uninstall xellgrid
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `xellgrid` within that folder.

### Packaging the extension

See [RELEASE](RELEASE.md)


Contributing
------------
All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome. See the
`Running from source & testing your changes`_ section above for more details on local qgrid development.

If you are looking to start working with the XellGrid codebase, navigate to the GitHub issues tab and start looking
through interesting issues.

Feel free to ask questions by submitting an issue with your question.
