// This file contains the javascript that is run when the notebook is loaded.
// It contains some requirejs configuration and the `load_ipython_extension`
// which is required for any notebook extension.

// Configure requirejs


declare global {
    interface Window {
        require: {
            config: any;
      };
    }
}
  


if (window.require) {
    window.require.config({
        map: {
            "*" : {
                "xellgrid": "nbextensions/xellgrid/index"
            }
        }
    });
}

// Export the required load_ipython_extension
export function load_ipython_extension(): void {};
