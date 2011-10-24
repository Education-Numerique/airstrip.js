var READY = "ready";

var _roxee_xhr = function(orsc, id, method, url, headers, data)
{
  var _xhr = new XMLHttpRequest();
  _xhr.id = id;
  _xhr.onreadystatechange = (function(){
    var t = _xhr;
    return function(){orsc.apply(t);};
  })();
  _xhr.open(method, url, true);
  for(var i in headers)
    _xhr.setRequestHeader(i, headers[i]);
  _xhr.send(data);
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

var honey = function(source){
  // For now, just let them play
/*  for(var x = 0; x < whitelist.length; x++)
    if(source.match(whitelist[x]))
      return true;
  return false;*/
  return true;
};

var receiver = function(e){
  var d = e.data;
  if(("id" in d) && ("method" in d) && ("url" in d)){
    new _roxee_xhr(bouncer, d.id, d.method, d.url, d.headers, d.data);
  }else{
    console.log("INVALID QUERY", d);
  }
}

_roxee_bridge.receiveMessage(receiver, honey);
_roxee_bridge.postMessage( READY, parent_url, parent );
