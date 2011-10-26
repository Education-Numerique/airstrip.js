var READY = "ready";

var _roxee_xhr = function(orsc, id, method, url, headers, data)
{
  var _xhr = new XMLHttpRequest();
  _xhr.id = id;
  _xhr.onreadystatechange = osrc;
/*  _xhr.onreadystatechange = (function(){
    var t = _xhr;
    return function(){orsc.apply(t);};
  })();*/
  // Open can fail in a number of circunstances
  try{
    _xhr.open(method, url, true);
    for(var i in headers)
      _xhr.setRequestHeader(i, headers[i]);
    _xhr.send(data);
  }catch(e){
    bouncer.apply(this);
  }
};

var parent_url = decodeURIComponent( document.location.hash.replace( /^#/, '' ) );

var bouncer = function(){
  var r = {
    id: this.id,
    readyState: this.readyState
  };
  try{
    r.status = this.status;
  }catch(e){
  }
  try{
    r.responseText = this.responseText;
  }catch(e){
  }
  try{
    r.responseHeaders = this.getAllResponseHeaders();
  }catch(e){
  }
  _roxee_bridge.postMessage( r, parent_url, parent );
};

var receiver = function(e){
  var d = e.data;
  if(("id" in d) && ("method" in d) && ("url" in d)){
    new _roxee_xhr(bouncer, d.id, d.method, d.url, d.headers, d.data);
  }else{
    console.log("INVALID QUERY", d);
  }
}

// Anyone can use this gate - the server will just enforce origin restriction based on app key host declarations
_roxee_bridge.receiveMessage(receiver, function(){return true;});
_roxee_bridge.postMessage( READY, parent_url, parent );
