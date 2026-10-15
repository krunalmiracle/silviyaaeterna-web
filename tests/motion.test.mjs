import assert from 'node:assert/strict';
import {test} from 'node:test';
const mod=await import('../assets/motion-state.js').catch(()=>({}));
test('motion permission stops for manual pause, reduced motion, hidden or offscreen',()=>{
 assert.equal(typeof mod.motionAllowed,'function');
 const base={paused:false,reduced:false,visible:true,inView:true};
 assert.equal(mod.motionAllowed(base),true);
 for(const change of [{paused:true},{reduced:true},{visible:false},{inView:false}]) assert.equal(mod.motionAllowed({...base,...change}),false);
});
