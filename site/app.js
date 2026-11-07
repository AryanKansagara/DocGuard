const $=id=>document.getElementById(id);
let selection=0;
async function show(name){
 const request=++selection;
 $('baseline').setAttribute('aria-pressed',String(name==='passing'));
 $('drift').setAttribute('aria-pressed',String(name==='drift'));
 try{
  const response=await fetch(name+'.json'); if(!response.ok)throw new Error('Report unavailable');
  const data=await response.json(); if(request!==selection)return;
  $('status').textContent=data.failures?'Needs attention':'Passed';
  $('status').className=data.failures?'bad':'good';
  $('checks').textContent=data.checks; $('failures').textContent=data.failures;
  $('description').textContent=name==='passing'?'Two authored examples match their documented output.':'Negative control: the code prints 5, while the documentation promises 4.';
  $('rows').replaceChildren();
  for(const row of data.results){
   const article=document.createElement('article');
   const heading=document.createElement('h3');heading.textContent=row.file+':'+row.line+' / '+row.id;
   const badge=document.createElement('span');badge.className='result '+(row.status==='passed'?'good':'bad');badge.textContent=row.status;
   const grid=document.createElement('div');grid.className='output';
   for(const [label,value] of [['Expected',row.expected],['Actual',row.actual]]){
    const wrap=document.createElement('div'),title=document.createElement('small'),pre=document.createElement('pre');
    title.textContent=label;pre.textContent=value??'—';wrap.append(title,pre);grid.append(wrap);
   }
   const hash=document.createElement('p');hash.className='hash';hash.textContent='Source fingerprint: '+row.source_sha256;
   article.append(heading,badge,grid,hash);$('rows').append(article);
  }
 }catch(error){$('status').textContent='Unavailable';$('rows').textContent=error.message;}
}
$('baseline').addEventListener('click',()=>show('passing'));
$('drift').addEventListener('click',()=>show('drift'));
show('passing');
