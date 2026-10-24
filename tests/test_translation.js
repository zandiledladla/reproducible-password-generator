/* Run from project folder: node tests/test_translation.js.
 * Uses real Python output as an independent cross-language oracle. */
'use strict';
const assert = require('node:assert/strict');
const {spawnSync} = require('node:child_process');
const {derivePassword, CATEGORIES} = require('../password_core.js');
const inputs = [['StudyDemo2026',8],['StudyDemo2026',24],['StudyDemo2026',128],
 ['Demo 🔐 é',24],[' Demo ',16],['e\u0301',32],['é'.repeat(512),24]];
(async()=>{
 const executable = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
 const child=spawnSync(executable,['-c',
  'import sys,json; from password_core import derive_password; print(json.dumps([derive_password(s,n) for s,n in json.load(sys.stdin)]))'],
  {input:JSON.stringify(inputs),encoding:'utf8'});
 assert.equal(child.status,0,child.stderr || 'Python process failed');
 const expected=JSON.parse(child.stdout);
 for(let i=0;i<inputs.length;i++) {
   const actual=await derivePassword(...inputs[i]);
   assert.equal(actual,expected[i]);
   assert.equal(actual.length,inputs[i][1]);
   for(const category of CATEGORIES) assert.ok([...actual].some(c=>category.includes(c)));
 }
 for(const [source,length] of [['',24],['  ',24],['demo',7],['demo',129],['demo',2.4],['é'.repeat(513),24]])
   await assert.rejects(()=>derivePassword(source,length));
 console.log('PASS: 7 cross-language vectors, lengths and categories, and 6 rejected invalid inputs.');
})().catch(error=>{console.error(error);process.exitCode=1;});
