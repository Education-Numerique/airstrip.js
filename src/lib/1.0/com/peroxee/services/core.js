/**
 * Search API
 *
 * Peroxee.services.search.movies(onSuccess, onFailure, question, [page, limit])
 * Peroxee.services.search.tvshows(onSuccess, onFailure, question, [page, limit])
 * Peroxee.services.search.people(onSuccess, onFailure, question, [page, limit])
 * Peroxee.services.search.episodes(onSuccess, onFailure, question, [page, limit])
 * Peroxee.services.search.all(onSuccess, onFailure, question, [page, limit])
 */
/**
 * Data API
 *
 * Peroxee.services.data.fetch(onSuccess, onFailure, id)
 */
/**
 * Autocomplete API
 *
 * Peroxee.services.autocomplete.movies(onSuccess, onFailure, question, [page, limit])
 * Peroxee.services.autocomplete.tvshows(onSuccess, onFailure, question, [page, limit])
 * Peroxee.services.autocomplete.people(onSuccess, onFailure, question, [page, limit])
 * Peroxee.services.autocomplete.episodes(onSuccess, onFailure, question, [page, limit])
 * Peroxee.services.autocomplete.all(onSuccess, onFailure, question, [page, limit])
 */
/**
 * User API
 *
 * Peroxee.services.users.profile.fetch(onSuccess, onFailure)
 * Peroxee.services.users.profile.update(onSuccess, onFailure, data)
 *
 * Peroxee.services.users.profile.fetch(onSuccess, onFailure, id)
 *
 * Peroxee.services.users.avatar.fetch(onSuccess, onFailure)
 * Peroxee.services.users.avatar.update(onSuccess, onFailure, data)
 *
 * Peroxee.services.users.avatar.fetch(onSuccess, onFailure, id)
 *
 * Peroxee.services.users.settings.fetch(onSuccess, onFailure)
 * Peroxee.services.users.settings.update(onSuccess, onFailure, data)
 *
 * Peroxee.services.users.preferences.fetch(onSuccess, onFailure)
 * Peroxee.services.users.preferences.update(onSuccess, onFailure, data)
 *
 * Peroxee.services.users.account.create(onSuccess, onFailure, infos)
 * Peroxee.services.users.account.validate(onSuccess, onFailure, email, code)
 * Peroxee.services.users.account.authenticate(onSuccess, onFailure)
 * Peroxee.services.users.account.activate(onSuccess, onFailure)
 * Peroxee.services.users.account.deactivate(onSuccess, onFailure)
 *
 * Peroxee.services.friends.sendRequest(onSuccess, onFailure, friendId)
 * Peroxee.services.friends.approveRequest(onSuccess, onFailure, friendId)
 * Peroxee.services.friends.denyRequest(onSuccess, onFailure, friendId)
 * Peroxee.services.friends.removeFriend(onSuccess, onFailure, friendId)
 * Peroxee.services.friends.pendingSentRequests(onSuccess, onFailure, page)
 * Peroxee.services.friends.pendingReceivedRequests(onSuccess, onFailure, page)
 * Peroxee.services.friends.fetch(onSuccess, onFailure, page)
 *
 * Undocumented (test usable):
 * XXX test only (should be denied): Peroxee.services.user.settings.fetch(onSuccess, onFailure, id)
 * XXX test only (should be denied): Peroxee.services.user.preferences.fetch(onSuccess, onFailure, id)
 * XXX test only (should be denied): Peroxee.services.user.friends.pendingSentRequests(onSuccess, onFailure, page)
 * XXX test only (should be denied): Peroxee.services.user.friends.pendingReceivedRequests(onSuccess, onFailure, page)
 */

// Error conditions
Peroxee.servicesErrors = {
  SERVICE_UNAVAILABLE: 1,
  
  WRONG_CREDENTIALS: 2,
  INVALID_SIGNATURE: 3,
  
  BAD_REQUEST: 4,
  MEANINGLESS_DATA: 5,
  UNAUTHORIZED: 6,
  MISSING: 7,
  UNSPECIFIED: 8,
  
  // Client is sending crap to the server! check your code Pavel!
  SHOULD_NOT_HAPPEN: 9
};

Peroxee.services = new (function(){

  var minimalRequester = function(method, host, port, url, params, payload, headers, catcher){
	var inme = new XMLHttpRequest();
//	var inme = new ___xxxdebugxhr();
	var c = catcher;

	var minimalCallback = function(){
		var error = null;
		var data = null;
	    // XXX Firefox 5 test fail
	    //if (inme.readyState == inme.DONE){
	    if (inme.readyState == 4) {
			// XXX must test redirections
	        if (inme.status >= 400){
	        	// options.data.status = inme.status;
	        	switch(inme.status){
					case 401:
						if(inme.getResponseHeader("WWW-Authenticate")){
							error = Peroxee.servicesErrors.WRONG_CREDENTIALS;
						}else{
							error = Peroxee.servicesErrors.INVALID_SIGNATURE;
						}
					break;
					case 402:
					case 403:
					case 405:
					case 501:
						error = Peroxee.servicesErrors.UNAUTHORIZED;
					break;
					case 404:
						error = Peroxee.servicesErrors.MISSING;
					break;
					case 406:
					// 407-410 should not happen
					case 400:
					case 411:
					case 412:
					case 413:
					case 414:
					case 415:
					case 416:
					case 417:
						error = Peroxee.servicesErrors.SHOULD_NOT_HAPPEN;
					break;
					case 500:
					case 503:
						error = Peroxee.servicesErrors.SERVICE_UNAVAILABLE;
					break;
					default:
						error = Peroxee.servicesErrors.UNSPECIFIED;
					break;
	        	}
	        }else if(inme.status == 0){
	        	// Failed to open
				error = Peroxee.servicesErrors.UNAUTHORIZED;
	        }else{
				try{
					if(inme.responseText)
	    				data = JSON.parse(inme.responseText);
				}catch(e){
					error = Peroxee.servicesErrors.MEANINGLESS_DATA;
					data = inme.responseText;
				}

	        }
			c(error, data, inme);
	    }else if(inme.readyState == inme.FAILED_OPENING){
	    	// Happens if the options returned with a deny ass
			error = Peroxee.servicesErrors.UNAUTHORIZED;
			c(error, data, inme);
	    }else if((inme.readyState != 1) && (inme.readyState != 2) && (inme.readyState != 3)){
/*
LOADING 3
HEADERS_RECEIVED 2
OPENED 1
*/
	    	console.log("Errrrrrr", inme.readyState);
	    }

	};

/*
DONE 4
FAILED_OPENING 10000
UNSENT 0
*/


	if(!url)
		url = "/";
	if(url.charAt(0) != "/")
		url = "/" + url;
	url = "http://" + host + (port ? (":" + port) : "") + url;
	var query = []
	if (params){
		for (var i in params) 
			query.push(encodeURIComponent(i) + "=" + encodeURIComponent(params[i]));
		if (query.length) 
			url += "?" + query.join("&");
	}


	// Prepare payload if any
	if(payload)
		try{
			if ((payload instanceof File) || (payload instanceof Blob)) {
				headers["Content-Type"] = payload.type;
			}else{
				payload = JSON.stringify(payload);
			}
		}catch(e){
			throw e;
		}

	inme.onreadystatechange = minimalCallback;
	inme.open(method, url, true);

	for(var i in headers)
		inme.setRequestHeader(i, headers[i]);

    inme.setRequestHeader('X-Requested-With', "XMLHttpRequest");

	try{
		inme.send(payload);
	}catch(e){
		console.log("Dramatic failure while sending", url, "with method", method, e);
		throw e;
	}
  };

  this.__debugMinimalRequester = minimalRequester;


  // Services names
  var AUTOCOMPLETE = "autocomplete";
  var DATA = "data";
  var USER = "users";
  var FRIENDS = "friends";
  var SEARCH = "search";
  
  // User sub commands
  var USER_PROFILE = "profile";
  var USER_AVATAR = "avatar";
  var USER_SETTINGS = "settings";
  var USER_PREFERENCES = "preferences";
  
  var USER_CMD_NEW = "new";
  var USER_CMD_VALIDATE = "validate";
  var USER_CMD_AUTHENTICATE = "authenticate";
  var USER_CMD_ACTIVATE = "activate";
  var USER_CMD_DEACTIVATE = "deactivate";
  var USER_CMD_SUPPRESS = "";
  
  var USER_CMD_REQUEST = "request";
  var USER_CMD_APPROVE = "approve";
  var USER_CMD_DENY = "deny";
  var USER_CMD_CANCEL = "cancel";
  var USER_CMD_REMOVE = "remove";
  var USER_CMD_PENDING = "pending";
  var USER_CMD_REQUESTS = "requests";
  var USER_CMD_FRIENDS = "friends";
  var USER_CMD_MUTUAL = "mutual";
  
  // Command types avalaible on most services
  var MOVIES = "movies";
  var TVSHOWS = "tvshows";
  var PEOPLE = "people";
  var EPISODES = "episodes";
  var NOTYPE = "";
  
  // Default limit for paginated stuff
  var DEFAULT_LIMIT = 20;



  
  // Private core-object that glue service queries to network ones (owned by a given service), holds error counter and handlers for *that* service,
  // along with the userId used to access it

  var _userId = "anonymous";
  var coreObject = function(serviceName, serviceErrorHandler){
    var _serviceName = serviceName;
    Object.defineProperty(this, "userId", {
      get: function(){
        return _userId;
      },
      enumerable: true
    });
    
    // XXX handle a too many error handler for a service 
    // XXX handle logout/change on another level
    // var _serviceErrorHandler = serviceErrorHandler;
    // var _failureCounter = 0;
    //this.failure = function(){return _failureCounter;};

    



    this.doQuery = function(options){
      // Default method
      var method = options.method;
      // Optional id
      var id = options.id;
      // Optional command
      var command = options.command;
      // Optional params
      var params = options.params;
      // Optional success
      var onSuccess = options.onSuccess;
      // Optional failure
      var onFailure = options.onFailure;
      // Optional payload
      var payload = options.payload;
      
      // XXX manu pense que c'est moins crade :)
      if (!command || !command.match(/^http:/)) {
        // Build-up URL with base config and current serviceName
        var url = "http://" + Peroxee.config.serviceHost + "/" + Peroxee.config.serviceVersion;
        if (_serviceName) 
          url += "/" + _serviceName;
        if (id) 
          url += "/" + id;
        if (command) 
          url += "/" + command;
        // XXX Manûß doesn't like trailing :)
        //			url += "/";
        // Build-up query string if any
        var query = []
        if (params) 
          for (var i in params) 
            query.push(encodeURIComponent(i) + "=" + encodeURIComponent(params[i]));
        
        if (query.length) 
          url += "?" + query.join("&");
      }
      else {
        url = command;
      }
      
      if (!options.headers) {
        options.headers = {
          "Accept": "application/json"
        };
      }
      // XXX do something serious!!!!
      options.headers["X-IID"] = "web";

			// Prepare payload if any
			if(method == "POST")
				try{
					if ((payload instanceof File) || (payload instanceof Blob)) {
						options.headers["Content-Type"] = payload.type;
						throw 'File Payload';
					}
					payload = JSON.stringify(payload);
					if(!("Content-Type" in options.headers))
						options.headers["Content-Type"] = "application/json";
				}catch(e){
					if(!("Content-Type" in options.headers))
						options.headers["Content-Type"] = "image/jpeg";
					// XXX async call onFailure on malformed request instead?
//					throw "Unable to serialize your freaxing data!";
				}


	    	options.debug = {
		    	url: url,
		    	method: method,
		    	payload: payload
			};


			// Inner XHR
			var inner = new XMLHttpRequest();

      // XXX doesn't work :/
      // inner.followRedirects = false;
      // XXX this is to beforwarded so that we can restart / replay
      inner.portOptions = options;
      inner.portOptions.coreObject = this;


			// XXX implement timeouts properly
			var callback = function(){
		    	options.error = null;
		    	options.data = null;
				options.inner = inner;
			    //if (inner.readyState == inner.DONE){
			    // XXX Firefox 5 test fail
			    if (inner.readyState == 4) {
			    	console.log("status", inner);
			    	console.log("status", inner.status);
			    	console.log("x--www", inner.getResponseHeader("WWW-Authenticate"));
			    	// XXX may not be the perfect place for that...
			    	options.data = {};
			    	try{
		              if(inner.getResponseHeader("X-UID"))
  				    	_userId = inner.getResponseHeader("X-UID");
			    	}catch(e){
			    		console.log("FAILED READING XUID");
			    	}

					// Errors might be driven by different conditions: 500+, 400+, XXX must test redirections
					// 400 -> bad request
					// 401 -> authent
					// 403 -> unauto
					// 404 -> pas de ressource
					// 405 -> bad request of some sort (method not allowed)
					// 500 -> Server error
			        if (inner.status >= 400){
			        	options.data.status = inner.status;
			        	// options.debug.body = inner.responseText;
			        	// XXX pass the url as well
			        	switch(inner.status){
							case 400:
                options.error = Peroxee.servicesErrors.BAD_REQUEST;
                var errorInfo = {code: 100, error: "GENERIC_ERROR"};
                try{
                  errorInfo = JSON.parse(inner.responseText);
                }catch(e){
                }
                options.data = errorInfo;
				        break;
							case 401:
								if(inner.getResponseHeader("WWW-Authenticate")){
									options.error = Peroxee.servicesErrors.WRONG_CREDENTIALS;
								}else{
									options.error = Peroxee.servicesErrors.INVALID_SIGNATURE;
								}
				                // options.onFailure(Peroxee.servicesErrors.);
							break;
							case 402:
							case 403:
							case 405:
							case 501:
								options.error = Peroxee.servicesErrors.UNAUTHORIZED;
							break;
							case 404:
								options.error = Peroxee.servicesErrors.MISSING;
							break;
							case 406:
							// 407-410 are not likely to happen
							case 411:
							case 412:
							case 413:
							case 414:
							case 415:
							case 416:
							case 417:
								options.error = Peroxee.servicesErrors.SHOULD_NOT_HAPPEN;
							break;
							case 500:
							case 503:
								options.error = Peroxee.servicesErrors.SERVICE_UNAVAILABLE;
							break;
							default:
								options.error = Peroxee.servicesErrors.UNSPECIFIED;
								console.log("UNSPECIFIED", inner.status, inner.responseText);
							break;
			        	}
//        				options.data = {body: inner.responseText, status: inner.status};
			        }else if(inner.status == 0){
	        				options.error = Peroxee.servicesErrors.UNAUTHORIZED;
			        }else{
	        			try{
	        				if(inner.responseText){
		        				options.data = JSON.parse(inner.responseText);
	        				}
	        			}catch(e){
	        				options.error = Peroxee.servicesErrors.MEANINGLESS_DATA;
	        				options.data.payload = inner.responseText;
	        			}

	        			// This is specific to the service (while the rest should be reusable)
/*			        	options.onSuccess(data);
	        			switch(options.command){
			        		case USER_CMD_AUTHENTICATE:
					        	options.onSuccess({});
			        		break;
			        		default:
			        		break;
			        	}*/
			        }

       				options.catcher(options);
//			    	options.catcher(inner, options);

			    }else if(inner.readyState == inner.FAILED_OPENING){
	  				options.error = Peroxee.servicesErrors.UNAUTHORIZED;
       				options.catcher(options);
			    }else{
			    }
			};
			inner.onreadystatechange = callback;
			try{
				console.log("Opening", url, "with method", method);
				inner.open(method, url, true);
			}catch(e){
				console.log("FAILLLLLUUUUUUUURE!!!! REPORT ME TO DMP", e);
			}
//			try{
//				if(payload)
//					inner.setRequestHeader('Content-Type', options.contentType);
			for(var i in options.headers){
				inner.setRequestHeader(i, options.headers[i]);
			}

/*			}catch(e){
				// Scream for "malformed query"
				var deferCall = function(ref){
					ref.callback.call(ref);
				};
				window.setTimeout(deferCall, 1, this);
			}*/
			try{
				console.log("Will send payload", payload);
				inner.send(payload);
			}catch(e){
				console.log("FAILLLLLUUUUUUUURE!!!! REPORT ME TO DMP", e);
			}
		};
	};

	// Private helper to init a request object
	var createOptions = function(catcher, onSuccess, onFailure, method, params, id, command, payload, headers){
		return {
			method: (method || "GET"),
			params: (params || {}),
			onSuccess: onSuccess,
			onFailure: onFailure,
			id: id,
			command: command,
			catcher: catcher,
			payload: payload,
			headers: headers
		};
	}

/* **************** */
	this.bootstrap = function(){
		// For now, this is the *library* key, not the implementer's
		DigestAuthentication.registerAppKey(Peroxee.config.keyId, Peroxee.config.secretKey);
		DigestAuthentication.persistent = false;
	};

	this.setCred = function(login, password){
		DigestAuthentication.registerCredentials(login, password);
	};


	var catcher = function(options){
        if (options.error){
            options.onFailure(options.error, options.data, options.inner);
        }else if(options.inner.status == 308){
            // Should replay baby
            try{
              // XXXdmp this is HORRIBLE - 308 may change service - we need a way to pass a block-level url
              options.inner.portOptions.params = {};
              options.inner.portOptions.id = null;
              options.inner.portOptions.command = options.inner.getResponseHeader("Location");// .match(/^http:\/\/[^\/]+\/(.+)/).pop();
              console.log(options.inner.portOptions.command);
              options.inner.portOptions.coreObject.doQuery(options.inner.portOptions);
            }catch(e){
            }
          
          options.catcher(options);
          //			    	options.catcher(inner, options);
        
        }else{
        	options.onSuccess(options.data, options.inner);
//        	        	console.log("hohohoh success", options, options.onSuccess);
        }
	};

	this.__debugCoreObject = coreObject;
	this.__debugCreateOptions = createOptions;
	this.__debugCatcher = catcher;

/* **************** */


	this.search = new (function(){
		// Base pattern
		var req = new coreObject(SEARCH);

		//	[GET] /1.0/search/(movies|tvshows|people|episodes)?/?q=request&start=0&limit=20
		var fetch = function(onSuccess, onFailure, question, page, limit, subset){
			limit = limit || DEFAULT_LIMIT;
			// REST API supports offsets, not pages, hence we need to cap that here
			var options = createOptions(catcher, onSuccess, onFailure, "GET", {
				page: (page  || "1"),
				q: question
			}, null, subset, null);
			req.doQuery(options);
		};

		this.movies = function(onSuccess, onFailure, question, page, limit){
			return fetch(onSuccess, onFailure, question, page, limit, MOVIES);
		};

		this.tvshows = function(onSuccess, onFailure, question, page, limit){
			return fetch(onSuccess, onFailure, question, page, limit, TVSHOWS);
		};

		this.people = function(onSuccess, onFailure, question, page, limit){
			return fetch(onSuccess, onFailure, question, page, limit, PEOPLE);
		};

		this.episodes = function(onSuccess, onFailure, question, page, limit){
			return fetch(onSuccess, onFailure, question, page, limit, EPISODES);
		};

		this.all = function(onSuccess, onFailure, question, page, limit){
			return fetch(onSuccess, onFailure, question, page, limit, NOTYPE);
		};

	})();


	this.autocomplete = new (function(){
		// Base pattern
		var req = new coreObject(AUTOCOMPLETE);

		// [GET] /1.0/autocomplete/(movies|tvshows|people|episodes)?/?q=request&limit=6
		var fetch = function(onSuccess, onFailure, question, subset, limit){
			var options = createOptions(catcher, onSuccess, onFailure, "GET", {
				page: ((subset * limit) || "0"),
				q: question
			}, null, subset, null);

			req.doQuery(options);
		};

		this.movies = function(onSuccess, onFailure, question, page, limit){
			return fetch(onSuccess, onFailure, question, page, limit, MOVIES);
		};

		this.tvshows = function(onSuccess, onFailure, question, page, limit){
			return fetch(onSuccess, onFailure, question, page, limit, TVSHOWS);
		};

		this.people = function(onSuccess, onFailure, question, page, limit){
			return fetch(onSuccess, onFailure, question, page, limit, PEOPLE);
		};

		this.episodes = function(onSuccess, onFailure, question, page, limit){
			return fetch(onSuccess, onFailure, question, page, limit, EPISODES);
		};

		this.all = function(onSuccess, onFailure, question, page, limit){
			return fetch(onSuccess, onFailure, question, page, limit, NOTYPE);
		};

	})();



	this.data = new (function(){
		// Base pattern
		var req = new coreObject(DATA);

		// [GET] /1.0/data/(movies|tvshows|people|episodes)?/a9260ca58e0f9494c6bbcf4801addfeac9c97995		
		// Subset should be optional... XXX Manuß
		this.fetch = function(onSuccess, onFailure, type, id){
			// XXX FIXME validate type here
			var options = createOptions(catcher, onSuccess, onFailure, "GET", {}, type, id, null);
			req.doQuery(options);
		};

	})();

	this.users = new (function(){
		// Base pattern
		var req = new coreObject(USER);

		// 	var createOptions = function(catcher, onSuccess, onFailure, method, params, id, command, payload){

		var miniController = function(command){
			this.update = function(onSuccess, onFailure, payload, id){
				if(!id)
					id = req.userId;
				var options = createOptions(catcher, onSuccess, onFailure, "POST", {}, id, command, payload);
				req.doQuery(options);
			};

			this.fetch = function(onSuccess, onFailure, id, params){
				if(!params)
					params = {};
				if(!id)
					id = req.userId;
				var options = createOptions(catcher, onSuccess, onFailure, "GET", params, id, command, null);
				req.doQuery(options);
			};

			/*var catcher = function(inner, options){
		        if (inner.status >= 400)
	                options.onFailure(inner.statusText);
		        else
		        	options.onSuccess(inner.responseText);
			};*/
		};

		// [GET] /1.0/users/37a749d808e46495a8da1e5352d03cae/profile
		// [POST] /1.0/users/37a749d808e46495a8da1e5352d03cae/profile
		this.profile = new miniController(USER_PROFILE);

		// [GET] /1.0/users/37a749d808e46495a8da1e5352d03cae/avatar
		// [POST] /1.0/users/37a749d808e46495a8da1e5352d03cae/avatar
		this.avatar = new miniController(USER_AVATAR, {w: 400, h: 400});

		this.avatar.BIG = 400;
		this.avatar.MEDIUM = 200;
		this.avatar.SMALL = 80;

		var old = this.avatar.fetch;

		this.avatar.fetch = function(onSuccess, onFailure, id){
			old.apply(this, [onSuccess, onFailure, id, {w: this.BIG, h: this.BIG}]);
		};


		this.avatar.getUrl = function(w, id){
			// XXX IMPLEMENT ME
			switch(w){
				case this.BIG:
				case this.MEDIUM:
				case this.SMALL:
				break;
				default:
					w = this.BIG;
				break;
			}
			var params = {w: w, h: w};
  			var url = "http://" + Peroxee.config.serviceHost + "/" + Peroxee.config.serviceVersion;
			url += "/" + USER;
  			if(id)
  				url += "/" + id;
			url += "?w=" + w + "&h=" + w;
			return url;
		};

		// [GET] /1.0/users/37a749d808e46495a8da1e5352d03cae/settings
		// [POST] /1.0/users/37a749d808e46495a8da1e5352d03cae/settings
		// Settings of the user that impact his profile, and ALL client applications
		this.settings = new miniController(USER_SETTINGS);

		//[GET] /1.0/users/37a749d808e46495a8da1e5352d03cae/preferences
		//[POST] /1.0/users/37a749d808e46495a8da1e5352d03cae/preferences
		// Settings for the *current* application - cannot be read if another APPID is there
		this.preferences = new miniController(USER_PREFERENCES);

		//- Account
		// [POST] /1.0/users/new
		//username (min=6, max=25)
		//email (min=6, max=35)
		//password (min=6, max=25)
		// [POST] /1.0/users/validate
		//email
		//code
		// [POST] /1.0/users/authenticate
		// [WIP] [POST] /1.0/users/37a749d808e46495a8da1e5352d03cae/activate
		// [WIP] [POST] /1.0/users/37a749d808e46495a8da1e5352d03cae/deactivate
		// [WIP] [DELETE] /1.0/users/37a749d808e46495a8da1e5352d03cae/?

		this.account = new (function(){
      this.__debugGetUserId = function(){
        return req.userId;
      }
      
      this.create = function(onSuccess, onFailure, username, email, password){
        var payload = {
          username: username,
          email: email,
          password: password
        };
        var options = createOptions(catcher, onSuccess, onFailure, "POST", {}, null, USER_CMD_NEW, payload);
        req.doQuery(options);
      };
      
      this.validate = function(onSuccess, onFailure, email, code){
        var payload = {
          code: code,
          email: email
        };
        var options = createOptions(catcher, onSuccess, onFailure, "POST", {}, null, USER_CMD_VALIDATE, payload);
        req.doQuery(options);
      };
      
      this.authenticate = function(onSuccess, onFailure){
        // Dumb payload
        var payload = {};
        var options = createOptions(catcher, onSuccess, onFailure, "GET", {}, null, USER_CMD_AUTHENTICATE, payload);
        req.doQuery(options);
      };
      
      this.activate = function(onSuccess, onFailure, id){
        if (!id) 
          id = req.userId;
        // Dumb payload
        var payload = {};
        var options = createOptions(catcher, onSuccess, onFailure, "POST", {}, id, USER_CMD_ACTIVATE, payload);
        req.doQuery(options);
      };
      
      this.deactivate = function(onSuccess, onFailure, id){
        if (!id) 
          id = req.userId;
        // Dumb payload
        var payload = {};
        var options = createOptions(catcher, onSuccess, onFailure, "POST", {}, id, USER_CMD_DEACTIVATE, payload);
        req.doQuery(options);
      };
      
      this.destroy = function(onSuccess, onFailure, id){
        if (!id) 
          id = req.userId;
        var options = createOptions(catcher, onSuccess, onFailure, "DELETE", {}, id, USER_CMD_SUPPRESS, null);
        req.doQuery(options);
      };
      
      /*
       this.confirmSuppress= function(onSuccess, onFailure, id, token){
       req.POST(id, "confirmSuppress", null, null, onSuccess, onFailure);
       };
       */
    })();
    
  })();
  
  
  this.friends = new (function(){
    // Base pattern
    var req = new coreObject(FRIENDS);
    
    //  var createOptions = function(catcher, onSuccess, onFailure, method, params, id, command, payload){
    
    var miniController = function(command){
      this.update = function(onSuccess, onFailure, payload, id){
        if (!id) 
          id = req.userId;
        var options = createOptions(catcher, onSuccess, onFailure, "POST", {}, id, command, payload);
        req.doQuery(options);
      };
      
      this.fetch = function(onSuccess, onFailure, id){
        if (!id) 
          id = req.userId;
        var options = createOptions(catcher, onSuccess, onFailure, "GET", {}, id, command, null);
        req.doQuery(options);
      };
      
      var catcher = function(inner, options){
        if (inner.status >= 400) 
          options.onFailure(inner.statusText);
        else 
          options.onSuccess(inner.responseText);
      };
    };
    
    //[POST] /1.0/users/37a749d808e46495a8da1e5352d03cae/request
    //[POST] /1.0/users/37a749d808e46495a8da1e5352d03cae/approve
    //[POST] /1.0/users/37a749d808e46495a8da1e5352d03cae/deny
    //[POST] /1.0/users/37a749d808e46495a8da1e5352d03cae/remove
    //[GET] /1.0/users/37a749d808e46495a8da1e5352d03cae/pending?start=0&limit=20
    //[GET] /1.0/users/37a749d808e46495a8da1e5352d03cae/requests?start=0&limit=20
    //[GET] /1.0/users/37a749d808e46495a8da1e5352d03cae/friends?start=0&limit=20
    
    this.sendRequest = function(onSuccess, onFailure, friendId){
      var payload = {};
      var options = createOptions(catcher, onSuccess, onFailure, "POST", {}, friendId, USER_CMD_REQUEST, payload);
      req.doQuery(options);
    };
    
    this.approveRequest = function(onSuccess, onFailure, friendId){
      var payload = {};
      var options = createOptions(catcher, onSuccess, onFailure, "POST", {}, friendId, USER_CMD_APPROVE, payload);
      req.doQuery(options);
    };
    
    this.denyRequest = function(onSuccess, onFailure, friendId){
      var payload = {};
      var options = createOptions(catcher, onSuccess, onFailure, "POST", {}, friendId, USER_CMD_DENY, payload);
      req.doQuery(options);
    };
    
    this.cancelRequest = function(onSuccess, onFailure, friendId){
      var payload = {};
      var options = createOptions(catcher, onSuccess, onFailure, "POST", {}, friendId, USER_CMD_CANCEL, payload);
      req.doQuery(options);
    };
    
    this.removeFriend = function(onSuccess, onFailure, friendId){
      var payload = {};
      var options = createOptions(catcher, onSuccess, onFailure, "POST", {}, friendId, USER_CMD_REMOVE, payload);
      req.doQuery(options);
    };
    
    this.getMutual = function(onSuccess, onFailure, page, limit, id){
      if (!id) 
        id = req.userId;
      
      limit = (limit || DEFAULT_LIMIT);
      var options = createOptions(catcher, onSuccess, onFailure, "GET", {
        page: (page || "1")
      }, id, USER_CMD_MUTUAL, {});
      req.doQuery(options);
    };
    
    this.pendingSentRequests = function(onSuccess, onFailure, page, limit, id){
      if (!id) 
        id = req.userId;
      
      limit = (limit || DEFAULT_LIMIT);
      var options = createOptions(catcher, onSuccess, onFailure, "GET", {
        page: (page  || "1")
      }, id, USER_CMD_REQUESTS, {});
      req.doQuery(options);
    };
    
    this.pendingReceivedRequests = function(onSuccess, onFailure, page, limit, id){
      if (!id) 
        id = req.userId;
      limit = (limit || DEFAULT_LIMIT);
      var options = createOptions(catcher, onSuccess, onFailure, "GET", {
        page: (page  || "1")
      }, id, USER_CMD_PENDING, {});
      req.doQuery(options);
    };
    
    this.fetch = function(onSuccess, onFailure, page, limit, id){
      limit = (limit || DEFAULT_LIMIT);
      if (!id) 
        id = req.userId;
      var options = createOptions(catcher, onSuccess, onFailure, "GET", {
        page: (page || "1")
      }, id, USER_CMD_FRIENDS, {});
      req.doQuery(options);
    };
    
  })();
})();


/*


 var onSuccess = function(data){


 try{


 data = JSON.parse(data);


 }catch(e){


 data = e;


 }


 console.log("success", data);


 };


 var onFailure = function(failureReason){


 console.log("fail: ", failureReason);


 };


 Peroxee.services.bootstrap();


 Peroxee.services.user.account.authenticate(onSuccess, onFailure);


 var page = 0;


 var limit = 3;


 var question = "Le dernier de";


 Peroxee.services.search.movies(onSuccess, onFailure, question, page, limit);


 Peroxee.services.search.tvshows(onSuccess, onFailure, question, page, limit);


 Peroxee.services.search.people(onSuccess, onFailure, question, page, limit);


 Peroxee.services.search.episodes(onSuccess, onFailure, question, page, limit);


 Peroxee.services.search.all(onSuccess, onFailure, question, page, limit);


 Peroxee.services.data.fetch(onSuccess, onFailure, "movies", "be5029cb697da40df89cd8d9396278b6e73a0387");


 */


/**


 * Data API


 *


 * Peroxee.services.data.fetch(onSuccess, onFailure, id)


 */


/**


 * Autocomplete API


 *


 * Peroxee.services.autocomplete.movies(onSuccess, onFailure, question, [page, limit])


 * Peroxee.services.autocomplete.tvshows(onSuccess, onFailure, question, [page, limit])


 * Peroxee.services.autocomplete.people(onSuccess, onFailure, question, [page, limit])


 * Peroxee.services.autocomplete.episodes(onSuccess, onFailure, question, [page, limit])


 * Peroxee.services.autocomplete.all(onSuccess, onFailure, question, [page, limit])


 */


/**


 * User API


 *


 * Peroxee.services.user.profile.fetch(onSuccess, onFailure)


 * Peroxee.services.user.profile.update(onSuccess, onFailure, data)


 *


 * Peroxee.services.user.profile.fetch(onSuccess, onFailure, id)


 *


 * Peroxee.services.user.avatar.fetch(onSuccess, onFailure)


 * Peroxee.services.user.avatar.update(onSuccess, onFailure, data)


 *


 * Peroxee.services.user.avatar.fetch(onSuccess, onFailure, id)


 *


 * Peroxee.services.user.settings.fetch(onSuccess, onFailure)


 * Peroxee.services.user.settings.update(onSuccess, onFailure, data)


 *


 * Peroxee.services.user.preferences.fetch(onSuccess, onFailure)


 * Peroxee.services.user.preferences.update(onSuccess, onFailure, data)


 *


 * Peroxee.services.user.account.create(onSuccess, onFailure, infos)


 * Peroxee.services.user.account.validate(onSuccess, onFailure, email, code)


 * Peroxee.services.user.account.authenticate(onSuccess, onFailure)


 * Peroxee.services.user.account.activate(onSuccess, onFailure)


 * Peroxee.services.user.account.deactivate(onSuccess, onFailure)


 *


 * Peroxee.services.user.friends.sendRequest(onSuccess, onFailure, friendId)


 * Peroxee.services.user.friends.approveRequest(onSuccess, onFailure, friendId)


 * Peroxee.services.user.friends.denyRequest(onSuccess, onFailure, friendId)


 * Peroxee.services.user.friends.removeFriend(onSuccess, onFailure, friendId)


 * Peroxee.services.user.friends.pendingSentRequests(onSuccess, onFailure, page, limit)


 * Peroxee.services.user.friends.pendingReceivedRequests(onSuccess, onFailure, page, limit)


 * Peroxee.services.user.friends.fetch(onSuccess, onFailure, page, limit, id)


 *


 * Undocumented (test usable):


 * XXX test only (should be denied): Peroxee.services.user.settings.fetch(onSuccess, onFailure, id)


 * XXX test only (should be denied): Peroxee.services.user.preferences.fetch(onSuccess, onFailure, id)


 * XXX test only (should be denied): Peroxee.services.user.friends.pendingSentRequests(onSuccess, onFailure, page, limit)


 * XXX test only (should be denied): Peroxee.services.user.friends.pendingReceivedRequests(onSuccess, onFailure, page, limit)


 */


