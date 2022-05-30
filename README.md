# XellGrid

XellGrid is a project branched out of the discontinued Qgrid project. The first release of XellGrid is to add support to JupyterLab with enhanced UI.  

Our goal is to create a powerful Jupyter enabled grid with rich "Excel" like UI features to enable regular users/analysts to benefit from 
the computational power of Python and cloud analytics through "low code/no code" principles.    

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
pip install -e .
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Rebuild extension Typescript source after making changes
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
