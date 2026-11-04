import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const wb=Workbook.create();
const sheets=JSON.parse(await fs.readFile('data.json','utf8'));
const chartColor='#193847';
const previews=process.argv[2];
if(previews) await fs.mkdir(previews,{recursive:true});
const col=i=>i<26?String.fromCharCode(65+i):'A'+String.fromCharCode(65+i-26);
for(const s of sheets){
  const sh=wb.worksheets.add(s.name);
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
}
wb.recalculate();
const check=await wb.inspect({kind:'table',range:'Decision brief!A5:I8',include:'values',tableMaxRows:4,tableMaxCols:9,maxChars:1400});
console.log(check.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:10},maxChars:400});console.log(errors.ndjson);
if(previews)for(const s of sheets){
  const preview=await wb.render({sheetName:s.name,range:'A1:'+col(Math.min(4,s.columns.length-1))+'10',scale:1,format:'png'});
  await fs.writeFile(previews+'/'+s.name+'.png',new Uint8Array(await preview.arrayBuffer()));
}
const file=await SpreadsheetFile.exportXlsx(wb);await file.save('hd2_data.xlsx');
