import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import * as xellgrid from './xellgrid.widget';
import * as base from '@jupyter-widgets/base';
/**
 * Initialization data for the xellgrid2 extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'xellgrid',
  autoStart: true,
  requires: [base.IJupyterWidgetRegistry],
  activate: (app: JupyterFrontEnd, widgets: base.IJupyterWidgetRegistry) => {
    widgets.registerWidget({
        name: 'xellgrid',
        version: '1.1.3', // todo: read from package.json
        exports: xellgrid
    });
    console.log('JupyterLab extension xellgrid2 is activated!');
  }
};

export default extension
