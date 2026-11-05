import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const exists=await fs.access('existing.xlsx').then(()=>true,()=>false);
const wb=exists ? await SpreadsheetFile.importXlsx(await FileBlob.load('existing.xlsx')) : Workbook.create();
const existingNames=new Set(exists ? (await wb.inspect({kind:'sheet',include:'name',maxChars:5000})).ndjson.split('\n').filter(Boolean).map(x=>JSON.parse(x).name) : []);
const sheets=JSON.parse(await fs.readFile('data.json','utf8'));
const chartColor='#193847';
const previews=process.argv[2];
if(previews) await fs.mkdir(previews,{recursive:true});
const col=i=>i<26?String.fromCharCode(65+i):'A'+String.fromCharCode(65+i-26);
for(const s of sheets){
  if(exists && !['Content timing','Timing evidence'].includes(s.name)){
    const sh=wb.worksheets.getItem(s.name);
    const width=s.columns.length,end=Math.max(6,5+s.rows.length);
    const oldRows=sh.getUsedRange().values;
    const current=sh.getRangeByIndexes(4,0,Math.max(1,s.rows.length)+1,width).values;
    const expected=[s.columns,...(s.rows.length?s.rows:[Array(width).fill(null)])];
    // Leave unchanged tabs intact. Refresh a dependent table if its source changed.
    if(JSON.stringify(current)!==JSON.stringify(expected) || (s.rows.length>12 && oldRows.length!==end)){
      const oldTable=sh.tables.items.find(t=>t.name===s.name.replaceAll(' ','')+'Table');
      oldTable?.delete();
      sh.getRangeByIndexes(4,0,Math.max(oldRows.length-4,end-4),width).clear({applyTo:'contents'});
      sh.getRangeByIndexes(4,0,expected.length,width).values=expected;
      const table=sh.tables.add('A5:'+col(width-1)+end,true,s.name.replaceAll(' ','')+'Table');
      table.style='TableStyleMedium2';
      for(let i=0;i<width;i++){
        const cells=sh.getRangeByIndexes(5,i,Math.max(1,s.rows.length),1),k=s.columns[i];
        if(s.dates.includes(k))cells.setNumberFormat('yyyy-mm-dd');
        if(s.percent.includes(k))cells.setNumberFormat('0.0%');
        if(s.editable.includes(k))cells.format.fill='#FFF1C5';
      }
    }
    if(s.name==='Prioritization')sh.getRange('A3').values=[[s.note]];
    if(s.review_revision)sh.getRange('B12').values=[[s.review_revision]];
    continue;
  }
  const old=existingNames.has(s.name) ? wb.worksheets.getItem(s.name) : null;
  if(old){
    // These two read-only export tabs are refreshed from the timing scorecard.
    old.tables.items.forEach(t=>t.delete());
    old.getUsedRange().clear({applyTo:'all'});
  }
  const sh=old ?? wb.worksheets.add(s.name);
  sh.showGridLines=false;
  const width=s.columns.length,end=Math.max(6,5+s.rows.length);
  sh.getRange('A2').values=[[s.title]];
  sh.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:chartColor};
  sh.getRange('A3').values=[[s.note]];
  sh.getRange('A3').format.font={name:'Arial',size:10,italic:true,color:'#435B65'};
  sh.getRangeByIndexes(4,0,1,width).values=[s.columns];
  if(s.rows.length) sh.getRangeByIndexes(5,0,s.rows.length,width).values=s.rows;
  const range='A5:'+col(width-1)+end;
  const table=sh.tables.add(range,true,s.name.replaceAll(' ','')+'Table');
  table.style='TableStyleMedium2';
  const body=sh.getRangeByIndexes(5,0,Math.max(s.rows.length,1),width);
  body.format.font={name:'Arial',size:10,color:chartColor};
  body.format.verticalAlignment='center';
  sh.getRangeByIndexes(4,0,1,width).format={fill:chartColor,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:26,verticalAlignment:'center'};
  for(let i=0;i<width;i++){
    const k=s.columns[i];
    const vals=s.rows.map(r=>String(r[i]??'').length);
    let w=Math.min(72,Math.max(15,k.length+5,...vals.map(v=>Math.min(52,v+2))));
    if(i===0)w=Math.max(w,22);
    const cells=sh.getRangeByIndexes(5,i,Math.max(s.rows.length,1),1);
    cells.format.columnWidth=w;
    if(s.dates.includes(k))cells.setNumberFormat('yyyy-mm-dd');
    if(s.percent.includes(k))cells.setNumberFormat('0.0%');
    if(k==='review_change_pp')cells.setNumberFormat('0.0" pp"');
    if(s.editable.includes(k))cells.format.fill='#FFF1C5';
    if(['summary','source_name','event_name','evidence_and_risk','option'].includes(k))cells.format.wrapText=true;
  }
  if(s.name==='Prioritization') body.format.rowHeight=44;
  if(['Event review','Releases','Events'].includes(s.name))body.format.rowHeight=33;
  if(s.rows.length>12)sh.freezePanes.freezeRows(5);
  if(s.review_revision){
    sh.getRange('A12:B12').values=[['Input revision',s.review_revision]];
    sh.getRange('A12:B12').format.font={name:'Arial',size:9,color:'#526873'};
  }
  for(const [row,text] of s.annotations??[]){
    sh.getRange('A'+row).values=[[text]];
    sh.getRange('A'+row).format.font={name:'Arial',size:10,color:chartColor};
  }
  if(s.name==='Content timing'){
    sh.getRange('A6:A13').format.columnWidth=27;
    sh.getRange('B6:B13').format.columnWidth=16;
    sh.getRange('C5:H5').format.wrapText=true;
    sh.getRange('C5:H5').format.rowHeight=40;
    sh.getRange('C6:H13').format.columnWidth=20;
    sh.getRange('A6:H13').format.rowHeight=24;
    sh.getRange('C6:C13').setNumberFormat('0" days"');
  }
}
wb.recalculate();
const check=await wb.inspect({kind:'table',range:'Decision brief!A5:I8',include:'values',tableMaxRows:4,tableMaxCols:9,maxChars:1400});
console.log(check.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:10},maxChars:400});console.log(errors.ndjson);
if(previews)for(const s of sheets.filter(s=>['Content timing','Timing evidence','Prioritization'].includes(s.name))){
  const view=s.name==='Content timing'?'A1:H25':s.name==='Prioritization'?'A1:F8':'A1:F13';
  const preview=await wb.render({sheetName:s.name,range:view,scale:1,format:'png'});
  await fs.writeFile(previews+'/'+s.name+'.png',new Uint8Array(await preview.arrayBuffer()));
}
const file=await SpreadsheetFile.exportXlsx(wb);await file.save('hd2_data.xlsx');
