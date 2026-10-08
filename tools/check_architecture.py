"""Check module references and compare gameplay with the Stage 1–2 baseline.

Run from any directory: python tools/check_architecture.py. Requires Git and Pillow.
"""
import ast, builtins, importlib, pathlib, symtable, sys, copy, random
from types import SimpleNamespace
root=pathlib.Path(__file__).resolve().parents[1]/'src';sys.path.insert(0,str(root))
# Validate every global reference in extracted modules without installing a linter.
paths=[root/'Game.py']+[p for pkg in ['engine','entities','input','levels','rendering'] for p in (root/pkg).glob('*.py')]
for path in paths:
 table=symtable.symtable(path.read_text(),str(path),'exec')
 globals_=set(table.get_identifiers())|set(dir(builtins))|{'__file__','__name__'}
 def check(t):
  for sym in t.get_symbols():
   if sym.is_global() and sym.is_referenced():
    assert sym.get_name() in globals_, (path,t.get_name(),sym.get_name())
  for child in t.get_children():check(child)
 check(table)
print(f'Static global-name check passed: {len(paths)} modules')
# Load the original function definitions only: never execute its GUI/camera imports or runApp.
import subprocess
source=subprocess.check_output(['git', 'show', 'ca02fca8c6433113bfd0906659ac82894ae1a7eb:src/Game.py'], cwd=root.parent, text=True)
tree=ast.parse(source)
original={'__file__':str(root/'Game.py')}
import os, math
from PIL import Image
from engine.collision import overlaps, player_hitbox, ghost_hitbox, hazard_rectangles
from engine.physics import advance_vertical
from engine.terrain import update_ground_levels
original.update(locals())
original["__file__"] = str(root/"Game.py")
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)]
exec(compile(ast.Module(body=functions,type_ignores=[]),'baseline','exec'),original)
from engine import state, runtime
from input import keyboard
from levels import state as levels
from entities import platforms,enemies
random.seed(15112)
comparisons=0
for mode in ['desktopInitialize','levelSelection','level0','level1','level2']:
 a=SimpleNamespace(instructionScreenActive=False,useHandGestures=False,levelUnlock=[0,1,2],levelLocked=[])
 original['initialstats'](a);b=copy.deepcopy(a)
 a.gamemode=b.gamemode=mode
 if mode in ['level0','level1','level2']:
  fn='level2initialstat' if mode=='level2' else 'level1initialstat'
  original[fn](a);getattr(levels,fn)(b)
 for i in range(500):
  keys=random.sample(['left','right','a','d'],random.randrange(3))
  original['onKeyHold'](a,keys);keyboard.onKeyHold(b,keys)
  if i%20==0:
   key=random.choice(['up','w','z','space','left','a'])
   original['onKeyPress'](a,key);keyboard.onKeyPress(b,key)
  original['onStep'](a);runtime.onStep(b)
  assert vars(a)==vars(b),(mode,i)
  comparisons+=1
print(f'Original-versus-refactor comparison passed: {comparisons} frame states across five screens')
