window.Peroxee = {
  config:{
    appHost: window.location.hostname,
    debug: true,
    serviceHost: "local.api.roxee.net:8771",
    //serviceHost: "snapshot.api.roxee.net",
    serviceVersion: "1.0",
    keyId: "01-TEST",
    secretKey: 'c3358d9200fc6ec0b563864521cabdbe180a4ea0',
  	//keyId: "TEST",
    //secretKey: '7c822bf13e729b809c2039fb4bfe9b3a6ce6437c',

    isWebkit: ('WebKitCSSMatrix' in window),
  	storage: {
  		authentication: 'DigestAuthenticationSession'
  	}
  }
};

/*

No key

"{ "time" : "1314788912", "error" : "'api#auth need api signature'", "code" : "1"}


"{"WWW-Authenticate": "Digest nonce=\"1314790748.39:F130:523e7a5c00655c780468c29b7ba8d630\", realm=\"dev@roxee\", algorithm=\"MD5\", opaque=\"71356353288832974615607729621987579082\", qop=\"auth\", stale=\"false\"", "Date": "Wed, 31 Aug 2011 11:39:08 GMT"}"

*/
