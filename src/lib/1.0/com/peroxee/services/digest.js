
(function() {

// This is a wrapper for the frame CORS hack that expose a "kind-of" XHR object

var roxHack = new (function(){
  var id = 0;
  var isReady = false;
  var debt = [];
  var ongoing = [];
  var frameHost = "http://api.roxee.net";
  var framePath = "/1.0/connect/gate";
  var framy;

  // Hook-on
  _roxee_bridge.receiveMessage(function(e){
    // Got a ready from the frame
    if(e.data == "ready"){
      // Frame is ready - anby debt there?
      isReady = true;
      for(var x = 0; x < debt.length; x++){
        debt[x].__postTrigger();
      }
      debt = [];
      return;
    }
    // Now, this is a real request return
    var myX = ongoing[e.data.id];
    var ar, re = {}, x, ti;
    for(var j in e.data){
      if(j != "id"){
        if(j == "responseHeaders"){
          // XXX need to parse that crap for real
          ar = e.data[j].split("\n");
          for (x = 0; x < ar.length; x++){
            if(ar[x]){
              ti = ar[x].match(/^([^:]+)[:]\s*(.+)/);
              ti.shift();
              myX.responseHeaders[ti.shift()] = ti.shift();
            }
          }
        }else{
          myX[j] = e.data[j];
        }
      }
    }
    myX.onreadystatechange();
  }, function(source){return source == frameHost;});

  // Register onload to embed the frame
  (function(){
    var x = window.onload;
    window.onload = function(){
      if(x)
        x();

      framy = document.createElement("iframe");
      framy.setAttribute("id", "_roxee_frame_hack");
      framy.setAttribute("style", "width: 0; height: 0; position: absolute; top: -1000px; left: -1000px;");
      framy.setAttribute("src", frameHost + framePath + "#" + document.location.href);
      document.body.appendChild(framy);
    };
  })();

  // Custom "XHR"
  var xhr = function(){
    var head = {}, method, url;
    var i = ++id;

    this.open = function(m, u) {
      method = m;
      url = u;
    };

    this.send = function(da) {
      var s = {"id": i, "method": method, "url": url, "headers": head, "data": da};
      if(isReady){
        ongoing[i] = this;
        _roxee_bridge.postMessage(JSON.stringify(s), frameHost + framePath, framy.contentWindow);
      }else{
        this.__postTrigger = function(){
          ongoing[i] = this;
          _roxee_bridge.postMessage(JSON.stringify(s), frameHost + framePath, framy.contentWindow);
        };
        debt.push(this);
      }
    };

    this.setRequestHeader = function(name, value) {
      head[name] = value;
    };

    // These will be altered by the crappy thingie from downstairs
    this.status;

    this.responseText;

    this.readyState;

    this.responseHeaders = {};

    this.getResponseHeader = function(name){
      if(name in this.responseHeaders)
        return this.responseHeaders[name];
      return false;
    };

    this.onreadystatechange = function(){
      
    };
  };

  return xhr;
})();


/**
 * Some private variables
 */
var _isDebuging = Peroxee.config.debug;
var _bugyWebKit = Peroxee.config.isWebkit;
var _persistentKey = Peroxee.config.storage.authentication;
// Store the original XHR
window.___xxxdebugxhr = XMLHttpRequest;

// var _orgXHR = XMLHttpRequest;

var _orgXHR = roxHack;

// Define the simili CORS User-Agent so that Varnish can set the response appropriately depending on the client capabilities
var _requestedWith = Peroxee.config.isWebkit ? 'XMLHttpRequest (body)' : 'XMLHttpRequest';



var _digestCredentials = {};
var _digestAuthorizations = {};

DigestAuthentication = {

  persistent: true,

  registerCredentials: function(username, password, host) {
    host = host || 'all';
    var credentials = _digestCredentials[host] || {};
    credentials.username = username;
    credentials.password = password;
    _digestCredentials[host] = credentials;
    //console.log("Here am i", _digestCredentials);
    // XXX dirty - that will destroy ALL current authorization, no matter what
    _digestAuthorizations = {};
  },

  registerUsername: function(username, host) {
    host = host || 'all';
    var credentials = _digestCredentials[host] || {};
    credentials.username = username;
    _digestCredentials[host] = credentials;
  },

  registerPassword: function(password, host) {
    host = host || 'all';
    var credentials = _digestCredentials[host] || {};
    credentials.password = password;
    _digestCredentials[host] = credentials;
  },

  registerHA1: function(ha1, host) {
    host = host || 'all';
    var credentials = _digestCredentials[host] || {};
    credentials.ha1 = ha1;
    _digestCredentials[host] = credentials;
//    this.saveSessionInfo();
  },

  reset: function(host) {
    host = host || 'all';
    delete _digestCredentials[host];
//    this.saveSessionInfo();
    _digestChalanges = {};
  },

/*  saveSessionInfo: function() {
    if (this.persistent) {
      persistentStorage.saveData(_persistentKey, JSON.stringify(_digestCredentials));
    }
  },

  loadSessionInfo: function() {
    if (this.persistent) {
      _digestCredentials = persistentStorage.loadData(_persistentKey);
    }
  }*/
};

// A simple helper to get access to credentials
var getCredentials = function(host) {
  host = host || 'all';
  var ret = _digestCredentials[host];
  return ret || false;
};

/*** ------------- ***/

/**
 * Appkey public API: registerAppKey
 */
DigestAuthentication.registerAppKey = function(keyId, secretKey) {
  _appKey = {keyId: keyId, secretKey: secretKey};
};

/**
 * AppKey internal mechanisms
 */
var _appKey = {};
var _appKeyDelta;

var _appKeySignature = function(keyId, secretKey, path, method, date) {
  var ts = _calculateDate(date);
  var ha = [keyId, secretKey, ts].join(':');
  ha = md5(ha);
  var signature = [method, path, ha].join(':');
  signature = md5(signature);
  var header = 'access Timestamp="' + ts + '", ';
  header += 'Signature="' + signature + '", ';
  header += 'KeyId="' + keyId + '", ';
  header += 'Algorithm="md5"';
  return header;
};

var _calculateDate = function(date) {
  var ts = Math.round(new Date().getTime() / 1000);
  if (date) {
    var sts = Date.parse(date) / 1000;
    _appKeyDelta = ts - sts;
    ts = sts;
  } else if (_appKeyDelta) {
    ts = ts - _appKeyDelta;
  }
  return ts;
};


// XXX move this outside
/*
document.addEventListener('DOMContentLoaded', function() {
  DigestAuthentication.loadSessionInfo();
}, false);
*/

/**
 * Helper meant to produce authentication headers 
 */
DigestAuthentication.Header = function() {
  var _username, _password, _ha1, _chalange, _cnonce, _nc;

  this.setCredantials = function(username, password) {
    _username = username;
    _password = password;
  };
  this.setHA1 = function(ha1) {
    _ha1 = ha1;
  };

  this.getHA1 = function() {
// XXX   return _ha1 || _generateHA1();
    return _generateHA1();
  };
  this.getRealm = function() {
    return _chalange.realm;
  };
  this.getUsername = function() {
    return _username;
  };

  this.parse = function(headers) {
    var header, key, value, _i, _len, _ref, _ref2;
    _chalange = {};
    _ref = headers.replace(/^Digest\s?/, "").split(/\s?,\s?/);
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      header = _ref[_i];
      if (header.match(/^nonce=/)) {
        _chalange.nonce = header.replace(/^nonce=\s?/, "").replace(/"/g, "");
      } else {
        _ref2 = header.split(/\s?=\s?/), key = _ref2[0], value = _ref2[1];
        _chalange[key] = value.replace(/"/g, "");
      }
    }
  };

  this.generate = function(url, method) {
    var auth, authArray, key;
    if (!_chalange) {
      throw new Error("No Digest Chalange");
    }
    auth = {
      uri: url,
      response: _generateResponse(url, method),
      username: _username,
      cnonce: _cnonce,
      realm: _chalange.realm,
      nonce: _chalange.nonce,
      opaque: _chalange.opaque,
      algorithm: _chalange.algorithm,
    };
    authArray = [];
    for (key in auth) {
      authArray.push("" + key + "=\"" + auth[key] + "\"");
    }
    authArray.push("qop=" + _chalange.qop);
    authArray.push("nc=" + _nc);
    return "Digest " + (authArray.join(', '));
  };

  this.reset = function() {
    _chalange = null;
    _nc = '00000000';
    _cnonce = _generateCnonce();
  };

  // private
  var _generateCnonce = function() {
    var number = Math.floor(Math.random()*100) + Math.floor(Math.random()*100)
      + Math.floor(Math.random()*100) + Math.floor(Math.random()*100);
    return md5(""+number);
  };
  var _generateHA1 = function() {
    if (_password && _chalange) {
      _ha1 = md5("" + _username + ":" + _chalange.realm + ":" + _password);
      _password = null;
    }
    return _ha1;
  };

  var _generateResponse = function(url, method) {
    if (method == null) { method = "GET"; }
    // XXX rape... _ha1 ||  _generateHA1
    var ha1 = _generateHA1();
    if (_chalange && ha1) {
      _incrementNC();
      var ha2 = md5("" + (method.toUpperCase()) + ":" + url);
      return md5("" + ha1 + ":" + _chalange.nonce + ":" + _nc + ":" + _cnonce
        + ":" + _chalange.qop + ":" + ha2);
    }
    return '';
  };
  var _incrementNC = function() {
    var l = _nc.length, n = parseInt(_nc),
        str = '' + (n+1);
    while (str.length < l) {
      str = '0' + str;
    }
    _nc = str;
  };

  this.reset();
};



/**
 * This is the public API that ought to be consumed by client code, once the engine is initialized
 */

DigestAuthentication.XMLHttpRequest = function() {
  // Store an original XHR
  var _xhr = new _orgXHR();

  // Holds our inside readyState wrapping
  var _readyState = this.UNSENT;


  // Self reference
  var self = this;



  var _headers = {}, _method, _url, _async;
  var _path, _host, _data;



  // Read-only accessors that map directly to the original XHR
  var _attrReaders = ['status', 'statusText', 'responseText', 'responseXML', 'upload',
    'UNSENT', 'OPENED', 'HEADERS_RECEIVED', 'LOADING', 'DONE'];

  for (var i = 0; i < _attrReaders.length; i++) {
    (function() {
      var attrName = _attrReaders[i];
      Object.defineProperty(self, attrName, {
        get : function(){ return _xhr[attrName]; },
        enumerable : true
      });
    })();
  };

  // Have a special failure status to catch correctly the "silent refuse to open" behavior
  Object.defineProperty(self, "FAILED_OPENING", {
    get : function(){ return 10000; },
    enumerable : true
  });

  // Read-write accessors that map directly to the original XHR
  var _attrAccessors = ['timeout', 'asBlob', 'followRedirects', 'withCredentials'];

  for (var i = 0; i < _attrAccessors.length; i++) {
    (function() {
      var attrName = _attrAccessors[i];
      Object.defineProperty(self, attrName, {
        get : function(){ return _xhr[attrName]; },
        set : function(value){ _xhr[attrName] = value; },
        enumerable : true
      });
    })();
  };

  // Methods that map directly to the original XHR
  this.overrideMimeType = function(mime) {
    return _xhr.overrideMimeType(mime);
  };

  this.abort = function() {
    return _xhr.abort();
  };

  this.getResponseHeader = function(name) {
    return _getResponseHeader(name);
  };

  this.getAllResponseHeaders = function() {
    return _xhr.getAllResponseHeaders();
  };

  // Methods that implement their own logic beyond the original XHR
  Object.defineProperty(this, "readyState", {
    get : function(){
      return _readyState;
    },
    enumerable : true
  });

  this.onreadystatechange = function() {};

  this.setRequestHeader = function(name, value) {
    try{
      _xhr.setRequestHeader(name, value);
      _headers[name] = value;
    }catch(e){
      // Right now, this happens only while trying to set headers on a non openable query (eg: TRACE / CONNECT in some browsers)
      console.log("Can't set request header - report me to dmp!", name, value);
    }
  };

  var _getResponseHeader = function(name){
    if (name === 'WWW-Authenticate') {
      name = 'X-WWW-Authenticate';
    }
    return _xhr.getResponseHeader(name);
  };

  var _buildChallenge = function(WWWAuthenticate) {
    var credentials = getCredentials(); // FIXME: support get by host
    if (!credentials)
      return;
    var Authorization = new DigestAuthentication.Header();
    Authorization.setCredantials(credentials.username, credentials.password);
    delete credentials.password;
    if (credentials.ha1)
      Authorization.setHA1(credentials.ha1);
    Authorization.parse(WWWAuthenticate);
    _digestAuthorizations[_host] = Authorization;
    DigestAuthentication.registerHA1(Authorization.getHA1()); // FIXME: support get by host
    return Authorization.generate(_path, _method);
  };


  var _sendRequestWithAuthorizationHeader = function(header) {
    var Authorization = _buildChallenge(header);
    if (!Authorization) {
      _readyState = _xhr.readyState;
      self.onreadystatechange.call(self);
      return;
    }

    var date = _getResponseHeader('Date');

    _xhr.onreadystatechange = function() {
//      if (_xhr.readyState === 4) {
      _readyState = _xhr.readyState;
      self.onreadystatechange.call(self);
//     }
    };
    _xhr.open(_method, _url, _async);
    _xhr.setRequestHeader('Authorization', Authorization);
    _xhr.setRequestHeader('X-Requested-With', _requestedWith + (_isDebuging ? " [debugger]" : ""));

    if (_appKey.keyId && _appKey.secretKey) {
      _xhr.setRequestHeader('X-Signature', _appKeySignature(_appKey.keyId, _appKey.secretKey, _path, _method, date));
    }

    for (name in _headers) {
      _xhr.setRequestHeader(name, _headers[name]);
    }
    _xhr.send(_data);
  };


  _xhr.onreadystatechange = function() {
    if (_xhr.readyState === 4 && _xhr.status === 401) {
      var WWWAuthenticate = _getResponseHeader('WWW-Authenticate');
      if (WWWAuthenticate) {
        _sendRequestWithAuthorizationHeader(WWWAuthenticate);
        return; 
      }
    }
    _readyState = _xhr.readyState;
    self.onreadystatechange.call(self);
  };

  this.open = function(method, url, async) {
    _method = method;
    _url = url;
    _async = async;
    // XXXdmp replace that with a proper URI parser
    _host = url.replace(/http:\/\//, '').split('/').shift();
    _path = url.replace(/http:\/\/[^\/]*/, '').split('?').shift();
    try{
      _xhr.open(method, url, async);
      _readyState = this.OPENED;
    }catch(e){
      console.log("something wrong happened", e);
      _readyState = this.FAILED_OPENING;
    }
  };

  this.send = function(data) {
    // Either the implementer forgot to 
    if (this.readyState == this.FAILED_OPENING) {
      // Should fail in an asynchronous manner
      var deferCall = function(ref){
        ref.onreadystatechange.call(ref);
      };
      window.setTimeout(deferCall, 1, this);

      return;
 //     throw new Error("INVALID_STATE_ERR: connection must be opened before send() is called");
    }
    _data = data;
    var Authorization = _digestAuthorizations[_host];
    if (Authorization) {
      _xhr.setRequestHeader('Authorization', Authorization.generate(_path, _method));
    }
    _xhr.setRequestHeader('X-Requested-With', _requestedWith);

    if (_appKey.keyId && _appKey.secretKey) {
      _xhr.setRequestHeader('X-Signature', _appKeySignature(_appKey.keyId, _appKey.secretKey, _path, _method));
    }
    try{
    _xhr.send(data);
    }catch(e){
      console.log("CALL DMP!!!!!!!!!!", e);
      throw e;
    }
  };

};

// Override native with our
window.XMLHttpRequest = DigestAuthentication.XMLHttpRequest;

})();
