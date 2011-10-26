/**
 * Basic ABNF
 * 
 * If you don't know what this is, you don't need it. If you think you should,
 * RTFRFC http://tools.ietf.org/html/rfc2234
 * 
 * @class ABNF RFC 2234 implem
 * @static
 * @name coreKit.ABNF2234
 */

var ABNF2234 = new (function() {
  /**
   * #@+
   * 
   * @private
   */
  this.alpha = 'A-Za-z';
  this.bit = '0-1';
  this.char = '\\x01-\\x7f';
  this.cr = '\\r';
  this.lf = '\\n';
  this.crlf = this.cr + this.lf;
  this.ctl = '[\\x00-\\x1F\\x7F]';
  this.digit = '0-9';
  this.dquote = '\\x22';
  this.hexdig = '[' + this.digit + 'A-Fa-f]';
  this.htab = '\\t';
  this.sp = ' ';
  this.wsp = '[' + this.sp + this.htab + ']';
  this.octet = '\\x00-\\xff';
  this.vchar = '\\x21-\\x7E';
  this.lwsp = '(?:' + this.wsp + '|' + this.crlf + this.wsp + ')*';
  /**
   * #@-
   * 
   * @private
   */
})();

