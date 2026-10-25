'use strict';
const $ = id => document.getElementById(id);
let grid, start, goal, result = null, ready = false, busy = false;
const rows=12, cols=18;
function reset(){
  grid=Array.from({length:rows},()=>Array(cols).fill(1));start=[5,1];goal=[5,16];
  if($('scenario').value==='detour'){
    for(let c=3;c<15;c++)grid[5][c]=5;
    for(let r=2;r<10;r++)if(r!==5&&r!==9)grid[r][9]=null;
  }
  if($('scenario').value==='blocked')for(let r=0;r<rows;r++)grid[r][9]=null;
  invalidate();
}
function invalidate(){
  result=null;$('download').disabled=true;$('step').disabled=true;
  for(const id of ['d-cost','a-cost'])$(id).textContent='—';
  $('d-count').textContent='Run a comparison to see results.';$('a-count').textContent='Manhattan distance heuristic';
  $('step-label').textContent='Run to explore the search trace.';
  if(ready)$('status').textContent='Map ready. Compare both algorithms.';
  render();
}
function key(p){return p.join(',');}
function render(){
  const active=result?.[$('view').value], step=Number($('step').value);
  const explored=new Set((active?.expanded||[]).slice(0,step).map(key));
  const path=new Set(active && step===active.expanded.length ? active.path.map(key):[]);
  const fragment=document.createDocumentFragment();
  for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){
    const p=[r,c], k=key(p), endpoint=k===key(start)?'S':k===key(goal)?'G':'';
    const button=document.createElement('button');button.type='button';button.className='cell';
    button.dataset.r=r;button.dataset.c=c;
    if(grid[r][c]===null)button.classList.add('wall');else if(grid[r][c]>1)button.classList.add('rough');
    if(explored.has(k))button.classList.add('explored');if(path.has(k))button.classList.add('path');
    if(endpoint)button.classList.add('endpoint');
    button.textContent=endpoint || (grid[r][c]>1?grid[r][c]:'');button.disabled=busy;
    button.setAttribute('aria-label',`Row ${r+1}, column ${c+1}: ${endpoint==='S'?'start':endpoint==='G'?'goal':grid[r][c]===null?'wall':'cost '+grid[r][c]}`);
    fragment.append(button);
  }
  $('grid').replaceChildren(fragment);
  if(active)$('step-label').textContent=`${step} of ${active.expanded.length} settled cells${step===active.expanded.length?' · complete':''}`;
}
$('grid').addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b||busy)return;
  const r=Number(b.dataset.r),c=Number(b.dataset.c),p=[r,c],brush=$('brush').value;
  if(brush==='start'||brush==='goal'){
    if(key(p)===key(brush==='start'?goal:start))return;
    grid[r][c]=1;if(brush==='start')start=p;else goal=p;
  }else {if(key(p)===key(start)||key(p)===key(goal))return;grid[r][c]=brush==='wall'?null:Number(brush);}
  invalidate();$('grid').children[r*cols+c].focus();
});
function showTrace(){if(!result)return;$('step').max=result[$('view').value].expanded.length;$('step').value=$('step').max;render();}
$('view').onchange=showTrace;$('step').oninput=render;
$('reset').onclick=reset;$('scenario').onchange=reset;
function setBusy(value){busy=value;$('run').disabled=value||!ready;$('reset').disabled=value;$('scenario').disabled=value;$('brush').disabled=value;render();}
const worker=new Worker('worker.js');
worker.onmessage=({data})=>{
  if(data.type==='ready'){ready=true;$('run').textContent='Compare routes ↗';$('status').textContent='Python ready. Your map stays in this browser.';setBusy(false);}
  if(data.type==='result'){
    result=data.result;setBusy(false);
    for(const [name,prefix] of [['dijkstra','d'],['astar','a']]){const s=result[name];$(prefix+'-cost').textContent=s.found?s.cost:'No route';$(prefix+'-count').textContent=`${s.expanded.length} settled · ${Math.max(0,s.path.length-1)} moves`;}
    $('status').textContent=result.astar.found?'Both searches completed. Explore their traces below.':'No route exists. Remove a wall or choose another scenario.';
    $('step').disabled=false;$('download').disabled=false;showTrace();
  }
  if(data.type==='error'){setBusy(false);$('status').textContent='Python could not complete: '+data.message+' Reload to retry.';}
};
worker.onerror=()=>{setBusy(false);$('status').textContent='Runtime could not load. Check your connection and reload.';};
$('run').onclick=()=>{if(!ready||busy)return;setBusy(true);$('status').textContent='Running both searches in Python…';worker.postMessage({type:'search',map:{grid,start,goal}});};
$('download').onclick=()=>{if(!result)return;const blob=new Blob([JSON.stringify({schema_version:1,map:{grid,start,goal},result},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='pathfinder-comparison.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
reset();worker.postMessage({type:'init'});
