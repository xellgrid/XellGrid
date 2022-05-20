import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import * as qgrid from './qgrid.widget';
import * as base from '@jupyter-widgets/base';
/**
 * Initialization data for the qgrid2 extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: 'qgrid',
  autoStart: true,
  requires: [base.IJupyterWidgetRegistry],
  activate: (app: JupyterFrontEnd, widgets: base.IJupyterWidgetRegistry) => {
    widgets.registerWidget({
        name: 'qgrid',
        version: '1.1.3', // todo: read from package.json
        exports: qgrid
    });
    console.log('JupyterLab extension qgrid2 is activated!');
  }
};

export default extension
