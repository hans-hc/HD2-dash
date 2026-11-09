"""Create a Jira import file from the editable, stable-ID master backlog."""
from common import ROOT,read_csv,write_csv
def main():
    rows=read_csv('jira/project_backlog.csv')
    rows=sorted(rows,key=lambda r:r['type']!='Epic')
    ids={r['local_id']:i for i,r in enumerate(rows,1)}
    if len(rows)!=len(ids):raise ValueError('Duplicate local issue ID')
    out=[]
    for r in rows:
        parent=ids.get(r['parent_id'],'')
        if r['parent_id'] and (not parent or parent>=ids[r['local_id']]):raise ValueError('Invalid parent: '+r['local_id'])
        if any(d not in ids for d in r['depends_on'].split('|') if d):raise ValueError('Unknown dependency in '+r['local_id'])
        body='\n'.join([r['purpose'],'Acceptance: '+r['acceptance'],'Owner: '+r['owner'],'Local evidence: '+r['evidence'],'Local work state: '+r['state'],
            'Priority rationale: '+r['rationale'],'Depends on: '+(r['depends_on'] or 'none recorded')])
        out.append({'Work item ID':ids[r['local_id']],'Work type':r['type'],'Parent':parent,'Summary':r['summary'],'Description':body,'Priority':r['priority'],'Labels':'hd2-local-'+r['local_id'].lower()})
    write_csv('jira/jira_import.csv',out,list(out[0]))
    print(len(rows),'import rows exported from master; no Jira write.')
if __name__=='__main__':main()
