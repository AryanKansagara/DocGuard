from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from docguard import report
root=Path(__file__).resolve().parents[1]
for name,folder in [('passing','docs'),('drift','fixtures')]:
    data=report((root/folder).rglob('*.md'),root/folder,True)
    (root/'site'/f'{name}.json').write_text(json.dumps(data,indent=2)+'\n')
    print(name,data['checks'],data['failures'])
