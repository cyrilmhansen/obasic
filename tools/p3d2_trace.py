#!/usr/bin/env python3
"""Run P3-D/2 natural Hatari CPU-disasm traces.

The debugger chain is the documented Hatari 2.6.1 pattern: :trace :once :file
breakpoints, CPU disassembly enabled at natural TEXT+$5D04, and disabled at
TEXT+$5E36. No FIFO stepping or memory/register injection is used.
"""
from __future__ import annotations
import argparse, os, shutil, subprocess, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROM=ROOT/'work/p3b/roms/tos306-tt-gb.img'; NVRAM=ROOT/'work/p3c/hatari-home/.config/hatari/hatari.nvram'
BIN={'e':ROOT/'work/extracted/p2/gfa-3.6/GFABASIC.PRG','d':ROOT/'work/extracted/p2/gfa-3.6tt/GFABASIC.PRG'}
def make_files(w, v, case):
 f=w/'fixtures'; t=w/'traces'; f.mkdir(parents=True); t.mkdir()
 stem=f'{v}-{case}'
 lines={
 'launch':f'b GemdosOpcode = $4B && OsCallParam = 0 :trace :once :file {f}/after-pexec.ini',
 'after-pexec':f'b pc = TEXT :trace :once :file {f}/after-entry.ini',
 'after-entry':f'b pc = "TEXT+$12DF6" :trace :once :file {f}/parser.ini',
 'parser':f'b pc = "TEXT+$1BD6" :trace :once :file {f}/dispatch.ini',
 'dispatch':f'b pc = "TEXT+$1BEC" :trace :once :file {f}/target.ini',
 'target':f'b pc = "TEXT+$5D04" :trace :once :file {f}/activate.ini',
 'activate':f'''cpureg\nsavebin {t}/{stem}-entry-ram.bin 0 0x400000\ntrace cpu_disasm\nb pc = "TEXT+$5E36" :trace :once :file {f}/deactivate.ini''',
 'deactivate':f'''cpureg\nsavebin {t}/{stem}-boundary-ram.bin 0 0x400000\ntrace none\nb all''',}
 for n,s in lines.items(): (f/(n+'.ini')).write_text(s+'\n')
 return f/'launch.ini',t

def type_case(wid, case):
 subprocess.run(['xdotool','windowactivate',wid,'key','shift+F9'],check=True); time.sleep(.3)
 subprocess.run(['xdotool','type','--clearmodifiers','--delay','90','PRINT '],check=True)
 keys=['shift+eacute','shift+q','shift+eacute'] if case=='print-a' else ['ampersand','plus','eacute']
 for k in keys:
  subprocess.run(['xdotool','key',k],check=True)
  time.sleep(.2)
 time.sleep(.3)
 subprocess.run(['xdotool','key','Return'],check=True)

def run(v,case,tag=None):
 name=f'{v}-{case}' if tag is None else f'{v}-{case}-{tag}'
 w=ROOT/'work/p3d2'/name;
 if w.exists(): raise RuntimeError(f'already exists: {w}')
 (w/'screenshots').mkdir(parents=True)
 home=w/'home'; (home/'.config/hatari').mkdir(parents=True); shutil.copyfile(NVRAM,home/'.config/hatari/hatari.nvram')
 drive=w/'drive'; shutil.copytree(ROOT/'work/p3c2'/f'drive-{v}',drive)
 ini,t=make_files(w,v,case); fifo=w/'hatari.fifo'; trace=t/'hatari.trace'; log=t/'hatari-debug.log'
 env=os.environ.copy(); env.update(HOME=str(home),LANG='fr_FR.UTF-8',SDL_VIDEODRIVER='x11')
 cmd=['hatari','--configfile',str(ROOT/'tools/hatari_gfa_scancode.cfg'),'--machine','tt','--tos',str(ROM),'--harddrive',str(drive),'--cmd-fifo',str(fifo),'--parse',str(ini),'--window','--trace','os_base,gemdos,bios,keymap,nvram','--trace-file',str(trace)]
 with log.open('w') as out:
  p=subprocess.Popen(['stdbuf','-oL',*cmd],cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT,text=True)
  try:
   wid=None; end=time.time()+35
   while time.time()<end and p.poll() is None:
    r=subprocess.run(['xdotool','search','--onlyvisible','--pid',str(p.pid)],capture_output=True,text=True)
    if r.returncode==0 and r.stdout.strip(): wid=r.stdout.strip().splitlines()[-1]; break
    time.sleep(.25)
   if not wid: raise RuntimeError('Hatari window did not appear')
   end=time.time()+40
   while time.time()<end:
    if trace.exists() and 'Pexec(0, "\\AUTO\\GFABASIC.PRG"' in trace.read_text(errors='replace'): break
    time.sleep(.25)
   else: raise TimeoutError('GFA BASIC startup not observed')
   time.sleep(1.5)
   type_case(wid,case)
   want=t/f'{v}-{case}-boundary-ram.bin'; end=time.time()+40
   while time.time()<end and not want.exists(): time.sleep(.2)
   if not want.exists(): raise TimeoutError('natural boundary not observed')
   time.sleep(2); subprocess.run(['import','-window',wid,str(w/'screenshots/after.png')],check=True)
  finally:
   p.kill(); p.wait(timeout=5)
 print(w)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('variant',choices='ed'); ap.add_argument('case',choices=['print-a','print-1plus2']); ap.add_argument('--tag'); a=ap.parse_args(); run(a.variant,a.case,a.tag)
if __name__=='__main__': main()
