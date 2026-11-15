#!/usr/bin/env python3
"""Extract bounded CPU-disassembly evidence from P3-D/2 Hatari logs."""
from __future__ import annotations
import argparse,json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LINE=re.compile(r'^([0-9a-f]{8})\s+([0-9a-f ]{4,24})\s{2,}(.+?)\s*$')
BR=re.compile(r'\b(b\w*|db\w*)\b.*\(([TF])\)')
CALL=re.compile(r'\b(bsr\.?[bwl]?|jsr|jmp|rts|rtd|rte)\b',re.I)
def parse(path):
 rows=[]; active=False
 for line in path.read_text(errors='replace').splitlines():
  if line.startswith('00014608 '): active=True
  if active:
   m=LINE.match(line)
   if m:
    pc=int(m.group(1),16); text=m.group(3); rows.append({'pc':f'0x{pc:08x}','text':text})
    if pc==0x14738: break
 return rows
def analyze(path):
 rows=parse(path); pcs=[int(x['pc'],16) for x in rows]
 debug=path.parent/'hatari-debug.log'
 boundary=debug.exists() and 'pc = $1473a' in debug.read_text(errors='replace')
 branches=[]; calls=[]; blocks=[]
 for i,r in enumerate(rows):
  text=r['text']; m=BR.search(text)
  if m: branches.append({'pc':r['pc'],'kind':m.group(1),'taken':m.group(2)=='T','text':text})
  c=CALL.search(text)
  if c: calls.append({'pc':r['pc'],'kind':c.group(1).lower(),'text':text})
  if i==0 or (i and pcs[i] not in (pcs[i-1]+2, pcs[i-1]+4, pcs[i-1]+6)):
   blocks.append({'entry':r['pc'],'reason':'target/return/nonlinear predecessor'})
 stem=path.parent.parent.name.replace('-retry2','')
 entry=path.parent/f'{stem}-entry-ram.bin'; boundary_ram=path.parent/f'{stem}-boundary-ram.bin'
 memory={}
 if entry.exists() and boundary_ram.exists():
  a=entry.read_bytes(); b=boundary_ram.read_bytes()
  memory={'entry_sha256':hashlib.sha256(a).hexdigest(),'boundary_sha256':hashlib.sha256(b).hexdigest(),'changed_bytes':sum(x!=y for x,y in zip(a,b)),'entry_target_body_sha256':hashlib.sha256(a[0x14608:0x14808]).hexdigest(),'boundary_target_body_sha256':hashlib.sha256(b[0x14608:0x14808]).hexdigest(),'conductor_writes':False}
 bconout=[]
 for line in path.read_text(errors='replace').splitlines():
  m=re.search(r'Bconout\(2, 0x([0-9A-Fa-f]{2})\)',line)
  if m: bconout.append('0x'+m.group(1).lower())
 return {'trace':str(path),'trace_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'instruction_count':len(rows),'pcs':[r['pc'] for r in rows],'instructions':rows,'basic_block_entries':blocks,'branches':branches,'calls_returns':calls,'boundary_reached':boundary,'target_only':bool(rows and pcs[0]==0x14608), 'last_cpu_pc':(f'0x{pcs[-1]:08x}' if pcs else None),'bconout_device2_bytes':bconout,'memory_snapshots':memory}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='work/p3d2'); ap.add_argument('--out',default='analysis/gfa/OUTPUT_TRACE_36_DATA.json'); a=ap.parse_args()
 root=ROOT/a.root; cases={}
 candidates=sorted(root.glob('*/traces/hatari.trace'))
 # Prefer the successful delayed-input retry for the one superseded failed attempt.
 chosen={}
 for p in candidates:
  name=p.parent.parent.name
  if name.startswith('prototype-') or name.endswith('-retry'): continue
  key=name.replace('-retry2','')
  if key not in chosen or name.endswith('-retry2'): chosen[key]=p
 for key,p in sorted(chosen.items()): cases[key]=analyze(p)
 out={'phase':'P3-D/2','method':'Hatari 2.6.1 trace cpu_disasm enabled at natural TEXT+$5D04 and disabled at TEXT+$5E36','cases':cases}
 Path(ROOT/a.out).write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({k:{'instruction_count':v['instruction_count'],'target_only':v['target_only'],'boundary_reached':v['boundary_reached'],'last_cpu_pc':v['last_cpu_pc'],'trace_sha256':v['trace_sha256']} for k,v in cases.items()},indent=2))
if __name__=='__main__': main()
