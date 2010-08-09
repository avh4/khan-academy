/*
 This is from the Caja corkboard demo which is available under the
 usual Caja source license:

    Copyright (C) 2010 Google Inc.
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    
    http://www.apache.org/licenses/LICENSE-2.0
    
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

 Since it is intended as part of a tutorial for Caja integration, if
 you are interested in reusing it under a license other than Apache 2.0,
 please let the Caja developers know.

*/ 
// Tools for handling the case where a web page contains many cajoled gadgets
// included inline, which should be executed only after the Caja runtime has
// been asynchronously loaded.
//
// First, call registerForScript(vdocId, moduleText) for each gadget, where
// vdocId is the id (string) of the DOM element to attach the gadget to, and
// moduleText is the JS source of a *cajoled* module. DO NOT PASS USER-SUPPLIED
// SCRIPT as moduleText, or you lose all security because it will just be
// eval()ed.
//
// After all scripts have been registered and the page has loaded (say, in
// <body onload="...">), call loadScripts(), which will load the Caja runtime
// and attach each script.
//
// @author kpreid@switchb.org

var registerForScript, loadScripts;
(function () {
  var scriptHooks = [];

  registerForScript = function (vdocId, moduleText) {
    scriptHooks.push([vdocId, moduleText]);
  }

  function go(caja) {
    for (var i = 0; i < scriptHooks.length; i++) {
      var id         = scriptHooks[i][0];
      var moduleText = scriptHooks[i][1];
      var sandbox = new caja.hostTools.Sandbox();
      sandbox.attach(document.getElementById(id));
      sandbox.runCajoledModuleString(moduleText);
    }
    scriptHooks = [];
  }
  
  loadScripts = function (server) {
    loadCaja(go, {
      debug: true,
      cajaServer: server
    });
  }
})();
