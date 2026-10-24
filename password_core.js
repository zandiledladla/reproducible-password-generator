/* COS738 algorithm v1: JavaScript translation of password_core.py.
 * Browser Web Crypto and Node webcrypto are supported. No third party libraries.
 * Preserve constants, UTF-8 encoding, and big-endian counter for reproducibility.
 */
(function (scope) {
  'use strict';
  const CATEGORIES = ['ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz',
    '0123456789', '!@#$%^&*()-_=+[]{};:,.<>/?'];
  const CHARSET = CATEGORIES.join('');
  const ITERATIONS = 200000;
  const encoder = new TextEncoder();
  function validateInputs(memorable, length) {
    const whitespace = '\u0009\u000a\u000b\u000c\u000d\u001c\u001d\u001e\u001f \u0085\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000';
    if (typeof memorable !== 'string' || !memorable || [...memorable].every(c => whitespace.includes(c)))
      throw new Error('Enter a memorable password, not just spaces.');
    // Reject unpaired surrogates instead of silently replacing them in UTF-8.
    for (let i = 0; i < memorable.length; i++) {
      const code = memorable.charCodeAt(i);
      if (code >= 0xD800 && code <= 0xDBFF) {
        const next = memorable.charCodeAt(++i);
        if (!(next >= 0xDC00 && next <= 0xDFFF)) throw new Error('Invalid Unicode input.');
      } else if (code >= 0xDC00 && code <= 0xDFFF) throw new Error('Invalid Unicode input.');
    }
    if (encoder.encode(memorable).length > 1024)
      throw new Error('Memorable password must be at most 1024 UTF-8 bytes.');
    if (!Number.isInteger(length) || length < 8 || length > 128)
      throw new Error('Output length must be a whole number from 8 to 128.');
  }
  async function derivePassword(memorable, length = 24) {
    validateInputs(memorable, length);
    const cryptoAPI = scope.crypto || (typeof require === 'function' ? require('node:crypto').webcrypto : null);
    if (!cryptoAPI || !cryptoAPI.subtle) throw new Error('Web Crypto unavailable. Use localhost or HTTPS in a modern browser.');
    const key = await cryptoAPI.subtle.importKey('raw', encoder.encode(memorable), 'PBKDF2', false, ['deriveBits']);
    const seed = new Uint8Array(await cryptoAPI.subtle.deriveBits({name: 'PBKDF2', hash: 'SHA-256',
      iterations: ITERATIONS, salt: encoder.encode(`COS738-PasswordGenerator-v1:${length}`)}, key, 256));
    let counter = 0, buffer = new Uint8Array(0), position = 0;
    async function choose(size) {
      const limit = 256 - (256 % size);
      while (true) {
        if (position === buffer.length) {
          const block = new Uint8Array(36);
          block.set(seed);
          new DataView(block.buffer).setUint32(32, counter++, false);
          buffer = new Uint8Array(await cryptoAPI.subtle.digest('SHA-256', block));
          position = 0;
        }
        const value = buffer[position++];
        if (value < limit) return value % size;
      }
    }
    const result = [];
    for (const category of CATEGORIES) result.push(category[await choose(category.length)]);
    while (result.length < length) result.push(CHARSET[await choose(CHARSET.length)]);
    for (let i = length - 1; i > 0; i--) {
      const other = await choose(i + 1);
      [result[i], result[other]] = [result[other], result[i]];
    }
    return result.join('');
  }
  const api = {derivePassword, validateInputs, CATEGORIES};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else scope.PasswordCore = api;
})(globalThis);
