/*
 * OutWit Kernel Copyright (c) OutWit Technologies 2008. All rights reserved.
 * 
 * Contributors: Disruptive Innovations SARL
 * 
 */

/**
 * @fileOverview Stuff to grab iris
 * @author dmp
 * @version 0.8
 */

/**
 * An IRI regexp stuffier thingier with fries.
 * 
 * Even if you know what this is, it's unlikely you should ever need to (not to
 * mention *want to*) read http://www.ietf.org/rfc/rfc3987 - if you're still
 * here: we use only the range in the Basic Multilingual Plane for the ucs, and
 * deliberately ignore anything in any of the planes from 1 to 16. I have no
 * idea how to do for these. Anyhow, planes 3 to 13 are not assigned, 15 and 16
 * are private use, 14 is defined as "special purpose" (no idea what this is),
 * and ignoring the SMP and SIP shouldn't be too much of a big deal...
 * 
 * @class IRI RFC 3987 implem
 * @static
 * @name coreKit.IRI3987
 */

var IRI3987 = new (function() {
  /**
   * #@+
   * 
   * @private
   */
  // ip addressing
  var decOctet = '(?:1[' + ABNF2234.digit + ']{2}|2[0-4][' + ABNF2234.digit
      + ']|25[0-5]|[1-9][' + ABNF2234.digit + ']|[' + ABNF2234.digit + '])';
  var ipv4address = decOctet + '\\.' + decOctet + '\\.' + decOctet + '\\.'
      + decOctet;
  var h16 = ABNF2234.hexdig + '{1,4}';
  var ls32 = '(?:' + h16 + '[:]' + h16 + '|' + ipv4address + ')';
  var ipv6addressc6 = '(?:' + h16 + '[:]){6}' + ls32;
  var ipv6addressc5 = '[:][:](?:' + h16 + '[:]){5}' + ls32;
  var ipv6addressc4 = h16 + '[:][:](?:' + h16 + '[:]){4}' + ls32;
  var ipv6addressc3 = '(?:' + h16 + '[:]){0,1}' + h16 + '[:][:](?:' + h16
      + '[:]){3}' + ls32;
  var ipv6addressc2 = '(?:' + h16 + '[:]){0,2}' + h16 + '[:][:](?:' + h16
      + '[:]){2}' + ls32;
  var ipv6addressc1 = '(?:' + h16 + '[:]){0,3}' + h16 + '[:][:]' + h16 + '[:]'
      + ls32;
  var ipv6addressc32 = '(?:' + h16 + '[:]){0,4}' + h16 + '[:][:]' + ls32;
  var ipv6addressc16 = '(?:' + h16 + '[:]){0,5}' + h16 + '[:][:]' + h16;
  var ipv6addressc0 = '(?:' + h16 + '[:]){0,6}' + h16 + '[:][:]';
  var ipv6address = '(?:' + ipv6addressc6 + '|' + ipv6addressc5 + '|'
      + ipv6addressc4 + '|' + ipv6addressc3 + '|' + ipv6addressc2 + '|'
      + ipv6addressc1 + '|' + ipv6addressc32 + '|' + ipv6addressc16 + '|'
      + ipv6addressc0 + ')';
  var unreserved = '[' + ABNF2234.alpha + ABNF2234.digit + '\\-._~';
  var subDelims = '!$&\'()*+,;=';
  var ipvfuture = 'v' + ABNF2234.hexdig + '+[.](?:' + unreserved + '|['
      + subDelims + ']|[:])+';
  var ipliteral = '\\[(?:' + ipv6address + '|' + ipvfuture + ')\\]';

  // genDelims = ':\\/?#[]@';
  // reserved = '[' + genDelims + subDelims + ']';
  // User info
  var pctEncoded = '%' + ABNF2234.hexdig + ABNF2234.hexdig;
  // XXX grrrrrr, yeah, that's utf8, so... goodbye astral plans
  // ucschar =
  // '\\xA0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF\\u10000-\\u1FFFD\\u20000-\\u2FFFD\\u30000-\\u3FFFD\\u40000-\\u4FFFD\\u50000-\\u5FFFD\\u60000-\\u6FFFD\\u70000-\\u7FFFD\\u80000-\\u8FFFD\\u90000-\\u9FFFD\\uA0000-\\uAFFFD\\uB0000-\\uBFFFD\\uC0000-\\uCFFFD\\uD0000-\\uDFFFD\\uE1000-\\uEFFFD';
  var ucschar = '\\xA0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF';
  var iunreserved = ABNF2234.alpha + ABNF2234.digit + ucschar + '\\-._~';
  var iuserinfo = '(?:[' + iunreserved + subDelims + ':]|' + pctEncoded + ')*';

  // Host
  var iregName = '(?:[' + iunreserved + subDelims + ']|' + pctEncoded + ')*';
  var ihost = '(?:' + ipliteral + '|' + ipv4address + '|' + iregName + ')';
  var port = '[' + ABNF2234.digit + ']*';

  // Auth
  var iauthority = '(?:(?:(' + iuserinfo + ')@)?(' + ihost + ')(?:[:](' + port
      + '))?)';

  // Fragment and query. XXXdmp Astral here? Is it actually working?
  var iprivate = '\\xE000-\\xF8FF\\xF0000-\\xFFFFD\\x100000-\\x10FFFD';
  var ipchar = '(?:[' + iunreserved + subDelims + ':@]|' + pctEncoded + ')';
  var iquery = '(?:' + ipchar + '|' + iprivate + '|[\\/?])*';
  var ifragment = '(?:' + ipchar + '|[\\/?])*';

  // Scheme... the easy bits
  var scheme = '[' + ABNF2234.alpha + '](?:[' + ABNF2234.alpha + ABNF2234.digit
      + '+.\\-])*';

  // Paths
  var isegment = ipchar + '*';
  var isegmentNz = ipchar + '+';
  var isegmentNzNc = '(?:[' + iunreserved + subDelims + '@]|' + pctEncoded
      + ')+';

  var ipathEmpty = ''; // errrrr... houston... 0<ipchar> wtf?
  var ipathAbempty = '(?:\\/' + isegment + ')*';
  var ipathAbsolute = '\\/(?:' + isegmentNz + '(?:\\/' + isegment + ')*)';
  var ipathNoscheme = isegmentNzNc + '(?:\\/' + isegment + ')*';
  var ipathRootless = isegmentNz + '(?:\\/' + isegment + ')*';

  var ihierPart = '\\/\\/' + iauthority + '(' + ipathAbempty + '|'
      + ipathAbsolute + '|' + ipathRootless + '|' + ipathEmpty + ')';
  /**
   * #@-
   * 
   * @private
   */
  /**
   * Stuff this into a regexp of your choice to grab iris
   * 
   * If used in a non-global context, will return separate matches for scheme,
   * userInfo, host, port, path, query and fragments parts
   * 
   * @name coreKit.IRI3987.IRI
   * @static
   * @type {String}
   */
  this.IRI = '(' + scheme + ')[:]' + ihierPart + '(?:[?](' + iquery
      + '))?(?:#(' + ifragment + '))?';

})();