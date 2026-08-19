import json, sys

for jf in ['TC-J04-00.json','TC-J04-01.json','TC-J04-02.json','TC-J04-03.json','TC-J04-04.json']:
    path = f'/home/work/22106610@sigma.sbrf.ru/giga/output/cases/J04-library-favorites-sync/{jf}'
    try:
        with open(path) as f:
            json.load(f)
        print(f'{jf}: OK')
    except json.JSONDecodeError as e:
        print(f'{jf}: ERROR at line {e.lineno} col {e.colno}: {e.msg}')
        with open(path) as f:
            lines = f.readlines()
        for i in range(max(0,e.lineno-3), min(len(lines), e.lineno+2)):
            marker = '>>> ' if i == e.lineno-1 else '    '
            print(f'{marker}{i+1}: {lines[i].rstrip()}')
