import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import * as xellgrid from './xellgrid.widget';
import { IJupyterWidgetRegistry } from '@jupyter-widgets/base';
import { CodeCell } from '@jupyterlab/cells';
// import { RenderMimeRegistry, standardRendererFactories as initialFactories } from '@jupyterlab/rendermime';
// import { SessionContext } from '@jupyterlab/apputils';
// import { ServerConnection, SessionManager, KernelManager, KernelSpecManager } from '@jupyterlab/services';
// import { KernelMessage } from '@jupyterlab/services';
import { INotebookTracker, } from '@jupyterlab/notebook';
// import { Widget } from '@lumino/widgets';
import {
  // IOutputPrompt,
  // IStdin,
  OutputArea,
  // OutputPrompt,
  // SimplifiedOutputArea,
  // Stdin
} from '@jupyterlab/outputarea';
import { ICommandPalette } from '@jupyterlab/apputils';
// import { ISettingRegistry } from "@jupyterlab/coreutils";

// import {
//   JSONObject,
//   // JSONValue,
//   // PartialJSONValue,
//   // PromiseDelegate,
//   // UUID
// } from '@lumino/coreutils';
// import { IExecuteReplyMsg } from '@jupyterlab/services/lib/kernel/messages';
/**
 * Initialization data for the xellgrid extension.
 */
const DEFAULT_SOURCE = `from xellgrid import add_tab
from IPython.display import display
display(add_tab())`
 
// const serverSettings = ServerConnection.makeSettings({
//   appendToken: true,
//   init: {
//     credentials: "include",
//     mode: 'cors',
//   }
// });
// const kernelManager = new KernelManager({
//   serverSettings
// });

// const specsManager = new KernelSpecManager({
//   serverSettings
// });

// const sessionManager = new SessionManager({
//   serverSettings,
//   kernelManager
// })

// const sessionContext = new SessionContext({
//   sessionManager,
//   specsManager,
//   name: 'xellgrid'
// });
// sessionContext.kernelPreference = { autoStartDefault: true }

// const rendermime = new RenderMimeRegistry({ initialFactories });
// const codeCell = new CodeCell({
//   rendermime,
//   model: new CodeCellModel({
//     cell: {
//       cell_type: 'code',
//       source: DEFAULT_SOURCE,
//       metadata: {
//       }
//     },
//     id: "2"
//   })
// });

// const cell = codeCell.initializeState();

const extension: JupyterFrontEndPlugin<void> = {
  id: 'xellgrid',
  autoStart: true,
  requires: [IJupyterWidgetRegistry, INotebookTracker, ICommandPalette],
  activate: (app: JupyterFrontEnd, widgets: IJupyterWidgetRegistry, 
    notebooks: INotebookTracker, palette: ICommandPalette) => {

    widgets.registerWidget({
      name: 'xellgrid',
      version: '1.1.3', // todo: read from package.json
      exports: xellgrid
    });

    const { commands } = app;

    let command = 'xellgrid-add_tab';
    let category = 'Tutorial';
    $("div#xellgrid-tabs").tabs();
    palette.addItem({command, category});
    commands.addCommand(command, {
      label: 'Add Xellgrid Tab',
      caption: 'Add one Xellgrid Tab',
      execute: (args) => {
        console.log('Hey')
        
        if(notebooks.currentWidget!==null){
          const notebookSession = notebooks.currentWidget.context.sessionContext;
          const cell = notebooks.activeCell
          // const rendermime = (cell as CodeCell).model.ren
          const code_output_area = (cell as CodeCell).outputArea
          console.log("rendermime: ", code_output_area.rendermime);
          OutputArea.execute(DEFAULT_SOURCE, code_output_area, notebookSession)
        }
      }});

    notebooks.currentChanged.connect((notebookTracker: INotebookTracker) =>{
      console.log("currentChanged emiited" );
      
    })
    notebooks.activeCellChanged.connect((notebookTracker: INotebookTracker) =>{
      const cell = notebookTracker.activeCell
      console.log("activeCellChanged emiited" );
      console.log("cell", cell );
    })
    notebooks.widgetAdded.connect((notebookTracker: INotebookTracker) =>{
      console.log("widgetAdded emiited" );
    })
    notebooks.widgetUpdated.connect((notebookTracker: INotebookTracker) =>{
      console.log("widgetUpdated emiited" );
    })

    

    // notebooks.currentChanged.connect((notebookTracker: INotebookTracker) => {
    //     // notebooks.currentWidget?.context
    //     if (!notebookTracker.currentWidget) {
    //       return;
    //     }
    //     console.log('current widget: ', notebookTracker.currentWidget);
        
    //     // const notebook = notebookTracker.currentWidget.content;
    //     // const notebookContext = notebookTracker.currentWidget.context;
    //     const notebookSession = notebookTracker.currentWidget.context.sessionContext;
    
    //     notebookTracker.currentWidget.sessionContext.connectionStatusChanged.connect((context: ISessionContext, status: any)=>{
    //       if(status==="connected"){
    //         console.log("kernel is ready");
    //         notebookTracker?.currentWidget?.sessionContext.ready
    //           .then(() =>
    //             notebookTracker?.currentWidget?.revealed.then(() => {
    //               const cell = notebooks.activeCell
    //               // const rendermime = (cell as CodeCell).model.ren
    //               const code_output_area = (cell as CodeCell).outputArea
    //               console.log("rendermime: ", code_output_area.rendermime);
    //               code_output_area.outputTracker.widgetAdded.connect((widgetTracker: IWidgetTracker)=>{
    //                 if (!widgetTracker.currentWidget){
    //                   return
    //                 }
    //               })
    //               OutputArea.execute(DEFAULT_SOURCE, code_output_area, notebookSession).then(()=>{
    //                 console.log("executed");
    //               })
    //             })
    //           ) 
  
    //             // console.log(`Executed add_tab`);
    //             // const cell = notebooks.activeCell
    //             // const code_output_area = (cell as CodeCell).outputArea
    //             // sessionContext.initialize().then(()=>{
    //             //   OutputArea.execute(DEFAULT_SOURCE, code_output_area, sessionContext)
    //             // })
    //             // console.log('JupyterLab extension xellgrid is activated!');
    //       }
    //     })
    //     // notebook?.model?.stateChanged.connect(async () => {
          
    //     // })


        
    //   })
  }
}


// function run(sessionContext:ISessionContext, code: string) {
//   let executeFn = OutputArea.execute;
//   OutputArea.execute = (
//     code: string,
//     output: OutputArea,
//     sessionContext: ISessionContext,
//     metadata?: JSONObject | undefined
//   ): Promise<IExecuteReplyMsg | undefined> => {
    
//     let promise;

//     try {

//       code = `${code}`;
      
//       promise = executeFn(code, output, sessionContext, metadata);
//       console.log("runnnnn");
      
//     }
//     catch (e) {

//       throw e;
//     }
//     finally {

//       OutputArea.execute = executeFn;
//     }

//     return promise;
//   }
//   // console.log(executeFn("print(1111)", ));
  
// }

export default extension
