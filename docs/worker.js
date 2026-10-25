/* Python runs in a worker so runtime initialization and search don't block the UI. */
let runtime;
self.onmessage = async ({data}) => {
  try {
    if (!runtime) {
      importScripts('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js');
      runtime = await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/'});
      const response = await fetch('engine.py');
      if (!response.ok) throw new Error('Could not load Python engine');
      await runtime.runPythonAsync(await response.text());
    }
    if (data.type === 'init') { self.postMessage({type:'ready'}); return; }
    runtime.globals.set('request_json', JSON.stringify(data.map));
    const result = JSON.parse(runtime.runPython('compare_json(request_json)'));
    self.postMessage({type:'result', result});
  } catch (error) { self.postMessage({type:'error', message:String(error.message || error)}); }
};
