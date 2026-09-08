import {test} from 'node:test';
import assert from 'node:assert/strict';
import {stateAt} from './src/state.mjs';
const captions=[0,7.098,17.326,19.6346667,28.6786667,31.606].map(start=>({start}));
test('a middle edit preserves positions and does not mistake identical C for reusable context',()=>{
 const before=stateAt(2,captions),during=stateAt(2.8,captions),after=stateAt(22,captions);
 assert.deepEqual(before.current,['A','B','C']);assert.deepEqual(during.current,['A','X','C']);
 assert.deepEqual(before.positions,during.positions);assert.deepEqual(during.positions,after.positions);
 assert.deepEqual(after.reuse,['A']);assert.deepEqual(after.reprocess,['X','C']);
 assert.deepEqual(after.old,['A','B','C']);
});
test('answer follows the explanatory voice and later examples follow their own lines',()=>{
 assert.deepEqual(stateAt(4,captions).reuse,[]);assert.equal(stateAt(12,captions).showContext,true);
 assert.equal(stateAt(18,captions).phase,'boundary');assert.equal(stateAt(30,captions).phase,'date');assert.equal(stateAt(33,captions).phase,'layout');
});
