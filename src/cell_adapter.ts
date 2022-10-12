import { SessionContext } from '@jupyterlab/apputils';
import { CodeCell, CodeCellModel } from '@jupyterlab/cells';
import { RenderMimeRegistry, standardRendererFactories as initialFactories } from '@jupyterlab/rendermime';
import { KernelManager, KernelSpecManager, ServerConnection, SessionManager } from '@jupyterlab/services';

const DEFAULT_SOURCE = `from IPython.display import display
for i in range(10):
    display('String {} added to the DOM in separated DIV.'.format(i))`

export class CellAdapter {
    private _codeCell: CodeCell;
    private _sessionContext: SessionContext;

    constructor(source: string) {
        const serverSettings = ServerConnection.makeSettings({
            appendToken: true,
            init: {
              credentials: "include",
              mode: 'cors',
            }
          });
          const kernelManager = new KernelManager({
            serverSettings
          });
          
          const specsManager = new KernelSpecManager({
            serverSettings
          });
          
          const sessionManager = new SessionManager({
            serverSettings,
            kernelManager
          })

          this._sessionContext = new SessionContext({
            sessionManager,
            specsManager,
            name: 'xellgrid'
          });
          this._sessionContext.kernelPreference = { autoStartDefault: true }
          
          const rendermime = new RenderMimeRegistry({ initialFactories });
          const codeCell = new CodeCell({
            rendermime,
            model: new CodeCellModel({
              cell: {
                cell_type: 'code',
                source: DEFAULT_SOURCE,
                metadata: {
                }
              },
              id: "2"
            })
          });
          this._codeCell = codeCell.initializeState()
          this._codeCell.activate();
    }

    get codeCell(): CodeCell {
        return this._codeCell;
      }
    
    get sessionContext(): SessionContext {
        return this._sessionContext;
    }

    execute = () => {
        CodeCell.execute(this._codeCell, this._sessionContext);
    }
}
