"""Explicitly opt-in documentation checks. Not an untrusted-code sandbox."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

FENCE = re.compile(r'^```(python|text) (check|expect)=([a-z][a-z0-9-]{0,40})\s*$')

def extract(text):
    blocks, active, body = {}, None, []
    for line, value in enumerate(text.splitlines(), 1):
        if active:
            if value == '```':
                kind, ident, start = active
                if (kind,ident) in blocks:
                    raise ValueError(f'line {start}: duplicate {kind} block {ident}')
                blocks[kind,ident] = {'text':'\n'.join(body)+'\n', 'line':start}
                active, body = None, []
            else:
                body.append(value)
        else:
            match = FENCE.fullmatch(value)
            if match:
                language, kind, ident = match.groups()
                if (language,kind) not in [('python','check'),('text','expect')]:
                    raise ValueError(f'line {line}: invalid language/block pairing')
                active = kind, ident, line
    if active:
        raise ValueError(f'line {active[2]}: unclosed check fence')
    ids = {ident for _,ident in blocks}
    for ident in ids:
        if ('check',ident) not in blocks or ('expect',ident) not in blocks:
            raise ValueError(f'{ident}: each check needs one expected-output block')
    return [{'id':ident, 'code':blocks['check',ident]['text'],
             'expected':blocks['expect',ident]['text'], 'line':blocks['check',ident]['line']}
            for ident in sorted(ids)]

def execute(code, timeout=2):
    # Only reviewed repository snippets may reach this function. -I is NOT isolation.
    with tempfile.TemporaryDirectory(prefix='docguard-') as directory:
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            process = subprocess.Popen([sys.executable,'-I','-S','-c',code], cwd=directory,
                env={'PATH':os.defpath}, stdin=subprocess.DEVNULL, stdout=out, stderr=err)
            try:
                process.wait(timeout=timeout)
                status = 'ok' if process.returncode == 0 else 'execution_error'
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                status = 'timeout'
            out.seek(0); err.seek(0)
            stdout, stderr = out.read(8193), err.read(8193)
            if len(stdout)>8192 or len(stderr)>8192:
                status = 'output_limit'
            return status, stdout[:8192].decode('utf-8',errors='replace'), stderr[:8192].decode('utf-8',errors='replace')

def check_text(text, execute_trusted=False):
    try:
        snippets = extract(text)
    except ValueError as error:
        return [{'id':'document','line':1,'status':'parse_error','message':str(error)}]
    results=[]
    for snippet in snippets:
        row = {'id':snippet['id'],'line':snippet['line'],
               'source_sha256':hashlib.sha256(snippet['code'].encode()).hexdigest()}
        try:
            ast.parse(snippet['code'])
        except SyntaxError:
            results.append({**row,'status':'syntax_error','message':'Python syntax is invalid.'})
            continue
        if not execute_trusted:
            results.append({**row,'status':'not_executed','message':'Syntax valid; execution requires --execute-trusted.'})
            continue
        status, stdout, stderr = execute(snippet['code'])
        if status == 'ok':
            status = 'passed' if stdout.rstrip('\n') == snippet['expected'].rstrip('\n') else 'output_mismatch'
        results.append({**row,'status':status,'expected':snippet['expected'],'actual':stdout,'stderr':stderr})
    return results

def slug(title):
    return re.sub(r'[^a-z0-9 -]','',title.strip().lower()).replace(' ','-')

def check_links(path, root):
    root=root.resolve(); results=[]
    for line, text in enumerate(path.read_text().splitlines(),1):
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)',text):
            if target.startswith(('https://','http://','mailto:')):
                continue
            file, _, anchor = target.partition('#')
            resolved=(path.parent/file).resolve() if file else path.resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                results.append({'line':line,'status':'outside_root','target':target}); continue
            if not resolved.is_file():
                results.append({'line':line,'status':'missing_link','target':target}); continue
            if anchor:
                headings={slug(x.lstrip('#').strip()) for x in resolved.read_text().splitlines() if x.startswith('#')}
                if anchor not in headings:
                    results.append({'line':line,'status':'missing_anchor','target':target})
    return results

def report(paths, root, trusted=False):
    rows=[]
    for path in sorted(paths):
        name=path.relative_to(root).as_posix()
        for item in check_text(path.read_text(),trusted)+check_links(path,root):
            rows.append({'file':name,**item})
    failures=sum(x['status'] not in ('passed','not_executed') for x in rows)
    return {'execution':'reviewed-local-process' if trusted else 'syntax-only',
            'checks':len(rows),'failures':failures,'results':rows}

def annotations(data):
    def escape(value):
        return str(value).replace('%','%25').replace('\r','%0D').replace('\n','%0A').replace(',','%2C').replace(':','%3A')
    return '\n'.join(f'::error file={escape(x["file"])},line={x["line"]}::{escape(x.get("id","link"))}: {escape(x["status"])}'
                     for x in data['results'] if x['status'] not in ('passed','not_executed'))

def release_notes(items):
    if not isinstance(items,list): raise ValueError('PR input must be a list')
    lines=['# Release Summary','']
    for item in items:
        if not isinstance(item,dict) or not isinstance(item.get('number'),int) or not isinstance(item.get('title'),str):
            raise ValueError('Each PR requires number and title')
        title=' '.join(item['title'].split())
        lines.append(f'- PR {item["number"]}: {title}')
    return '\n'.join(lines)+'\n'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    parser.add_argument('--execute-trusted',action='store_true',help='Execute only reviewed repository code; not safe for untrusted PRs.')
    parser.add_argument('--json',type=Path)
    parser.add_argument('--annotations',action='store_true')
    args=parser.parse_args()
    root=args.root.resolve()
    if not root.is_dir(): parser.error('root must be an existing directory')
    data=report(root.rglob('*.md'),root,args.execute_trusted)
    if args.json: args.json.write_text(json.dumps(data,indent=2)+'\n')
    print(annotations(data) if args.annotations else json.dumps(data,indent=2))
    return int(data['failures']>0)

if __name__=='__main__':
    raise SystemExit(main())
