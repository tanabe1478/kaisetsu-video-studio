// Semantic state, independent from drawing. All timestamps use the actual audio.
export const clamp=x=>Math.max(0,Math.min(1,x));
export function stateAt(t,captions){
 const starts=captions.map(c=>c.start);
 const phase=t<starts[1]?'question':t<starts[2]?'context':t<starts[4]?'boundary':t<starts[5]?'date':'layout';
 const changed=t>=2.5;
 return {phase,changed,old:['A','B','C'],current:['A',changed?'X':'B','C'],positions:[260,550,840],reuse:phase==='boundary'?['A']:[],reprocess:phase==='boundary'?['X','C']:[],showContext:phase==='context',changeProgress:clamp((t-2.5)/.5)};
}
