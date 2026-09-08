import React from 'react';
import {AbsoluteFill,useCurrentFrame,useVideoConfig,interpolateColors} from 'remotion';
import {stateAt,clamp} from './state.mjs';

const ink='#173d35',cream='#f6f3e9',white='#f8faf0',muted='#a8bfb2',green='#b7eb93',orange='#ffbc88';
const Text=({x,y,children,size=25,fill=white,anchor='start',...rest}:any)=><text x={x} y={y} fontSize={size} fill={fill} textAnchor={anchor} {...rest}>{children}</text>;
const Box=({x,y,label,oldLabel,mix=1,detail,color=muted,w=230}:any)=><g><rect x={x} y={y} width={w} height={76} rx={12} fill={color===muted?'#254e43':color===green?'#31553f':'#604838'} stroke={color} strokeWidth={2}/>{oldLabel&&<Text x={x+w/2} y={y+46} size={36} anchor="middle" fill={color} opacity={1-mix}>{oldLabel}</Text>}<Text x={x+w/2} y={y+46} size={36} anchor="middle" fill={color} opacity={mix}>{label}</Text>{detail&&<Text x={x+w/2} y={y+104} size={19} anchor="middle" fill={color}>{detail}</Text>}</g>;
export function PrefixLesson({captions,globalStart}:any){
 const frame=useCurrentFrame(),{fps}=useVideoConfig(),t=frame/fps,s=stateAt(t,captions);
 const active=captions.find((c:any)=>t>=c.start&&t<c.end);
 const guide=active?.character==='guide';
 const label=s.phase==='question'?'Cは同じ。計算も使い回せる？':s.phase==='context'?'同じ文字でも、そこまでの文脈が違う':s.phase==='boundary'?'再利用候補は、先頭から一致するAまで':s.phase==='date'?'先頭への追加も、一致する範囲を変える':'固定の情報を前に、変わる情報を後ろに';
 const boundary=s.phase==='boundary';
 const scan=clamp((t-captions[2].start)/1.2);
 return <AbsoluteFill style={{background:cream,fontFamily:'Hiragino Sans, sans-serif',color:ink}}>
 <div style={{position:'absolute',left:48,top:28,fontSize:16,letterSpacing:3,fontWeight:700}}>PROMPT CACHE / 03　先頭一致</div>
 <div style={{position:'absolute',left:48,top:62,fontSize:35,fontWeight:800}}>同じ「C」でも、再利用できるとは限らない</div>
 <svg width="1280" height="720" style={{position:'absolute',inset:0,fontFamily:'Hiragino Sans, sans-serif'}}>
 <defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill={orange}/></marker></defs>
 <rect x="48" y="127" width="1184" height="408" rx="20" fill={ink}/>
 <Text x={80} y={169} size={24} fill={white}>{label}</Text>
 {['question','context','boundary'].includes(s.phase)?<g>
 <Text x={85} y={252} size={20} fill={muted}>前回の入力</Text><Text x={85} y={390} size={20} fill={white}>今回の入力</Text>
 {s.positions.map((x:number,i:number)=><g key={i}>
 <Box x={x} y={203} label={s.old[i]}/>
 <line x1={x+115} x2={x+115} y1={289} y2={329} stroke={i===1&&s.changed?orange:muted} strokeWidth="2" strokeDasharray={i===1?'5 5':undefined}/>
 <Text x={x+135} y={315} size={17} fill={i===1&&s.changed?orange:muted}>{i===1&&s.changed?'変更':'同じ'}</Text>
 <Box x={x} y={343} label={s.current[i]} oldLabel={i===1&&s.changed?"B":undefined} mix={i===1&&s.changed?s.changeProgress:1} color={boundary?(i===0?green:orange):i===1&&s.changed?interpolateColors(s.changeProgress,[0,1],[muted,orange]):muted}/>
 </g>)}
 {s.showContext&&<g opacity={clamp((t-captions[1].start)/.6)}>
 <path d="M 280 198 L 280 189 L 760 189 L 760 198" fill="none" stroke={orange} strokeWidth="2"/>
 <path d="M 280 436 L 280 446 L 760 446 L 760 436" fill="none" stroke={orange} strokeWidth="2"/>
 <Text x={520} y={482} anchor="middle" size={21} fill={orange}>A・B を読んだC ≠ A・X を読んだC</Text>
 <Text x={958} y={478} anchor="middle" size={18} fill={muted}>文字の一致だけでは不足</Text>
 </g>}
 {boundary&&<g opacity={scan}>
 <rect x={248} y={333} width={254} height={98} rx={15} stroke={green} strokeWidth={3} fill="none"/>
 <path d="M 526 324 L 526 441" stroke={orange} strokeDasharray="7 6" strokeWidth="2"/>
 <Text x={375} y={468} anchor="middle" size={23} fill={green}>再利用の候補</Text>
 <path d={`M 555 441 H ${555+510*scan}`} stroke={orange} strokeWidth="3" markerEnd="url(#arrow)"/>
 <Text x={810} y={477} anchor="middle" size={23} fill={orange}>Xと、その後のCは再処理</Text>
 </g>}
 {s.phase==='question'&&<Text x={1090} y={400} size={40} fill={orange}>?</Text>}
 </g>:s.phase==='date'?<g>
 <Text x={85} y={254} size={20} fill={muted}>前回</Text><Text x={85} y={386} size={20}>今回</Text>
 {['A','B','C'].map((v,i)=><Box key={v} x={260+i*245} y={210} w={205} label={v}/>)}
 {['日付','A','B','C'].map((v,i)=>{const q=clamp((t-captions[4].start)/.8);const initial=i===0?260:260+(i-1)*245;return <g key={v} opacity={i===0?clamp((q-.85)/.15):1}><Box x={initial+(260+i*218-initial)*q} y={342} w={194} label={v} color={orange}/></g>})}
 <Text x={660} y={478} anchor="middle" size={24} fill={orange}>先頭から変わる → 元の接頭辞とは一致しない</Text>
 </g>:<g opacity={clamp((t-captions[5].start)/.5)}>
 <Text x={85} y={224} size={21} fill={muted}>入力の配置</Text>
 <Box x={180} y={276} w={285} label="固定の説明" detail="毎回同じ内容" color={green}/>
 <Box x={495} y={276} w={285} label="会話の履歴" detail="共通部分を保つ" color={green}/>
 <Box x={810} y={276} w={285} label="今回の情報" detail="日付・新しい依頼" color={orange}/>
 <path d="M 190 421 H 1090" stroke={muted} strokeWidth="2"/>
 <Text x={190} y={458} size={22} fill={green}>安定した先頭</Text><Text x={1090} y={458} anchor="end" size={22} fill={orange}>変化する末尾</Text>
 </g>}
 <Text x={1202} y={519} anchor="end" size={14} fill={muted}>模式図 · 保持状態など、他の成立条件は省略</Text>
 </svg>
 <div style={{position:'absolute',left:48,top:553,width:1184,height:110,borderRadius:16,background:'#e9e7de',display:'flex',alignItems:'center',padding:'16px 24px',boxSizing:'border-box',gap:22}}>
 <div style={{flex:'0 0 125px',fontSize:18,fontWeight:700,color:ink,display:'flex',alignItems:'center',gap:12}}><svg width="38" height="44" viewBox="0 0 38 44"><circle cx="19" cy="15" r="13" fill={guide?green:'#efb4bd'}/><path d="M 3 44 Q 3 29 19 29 Q 35 29 35 44" fill={guide?green:'#efb4bd'}/><circle cx="14" cy="14" r="1.7" fill={ink}/><circle cx="24" cy="14" r="1.7" fill={ink}/><ellipse cx="19" cy="21" rx="3" ry={active&&frame%8<4?3:1} fill={ink}/></svg>{active?(guide?'解説役':'質問役'):''}</div>
 <div style={{fontSize:27,lineHeight:1.5,fontWeight:600,flex:1}}>{active?.text??''}</div>
 </div>
 <div style={{position:'absolute',left:50,bottom:17,fontSize:13,color:'#50675d'}}>VOICEVOX：四国めたん・ずんだもん　｜　図・話者アイコン：自作SVG</div>
 <div style={{position:'absolute',right:50,bottom:17,fontSize:13,color:'#50675d'}}>{globalStart===undefined?`先頭一致の説明 · ${Math.floor(t).toString().padStart(2,'0')} / 40秒`:`${Math.floor((globalStart+t)/60)}:${String(Math.floor(globalStart+t)%60).padStart(2,'0')} / 20:03`}</div>
 </AbsoluteFill>;
}

