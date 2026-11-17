"""Converte os dados da página partilhada "Intervenções dos Animais" (coleções animais, extras, meta)
num ficheiro analises_marrocos.js que a App de Alocação lê ao abrir.

Uso: python3 gerar_analises.py <pasta_com_json> <saida.js>
A pasta tem o formato do ArtifactData out_dir: animais/*.json, extras/*.json, meta/import.json
"""
import json, glob, os, re, sys, datetime

src, dst = sys.argv[1], sys.argv[2]
TESTS = [('ibr', r'ibr|bohv'), ('bvd', r'bvd'), ('ehd', r'ehd|hemorr'), ('sbv', r'schmall'),
         ('bru', r'brucel|rosa bengala|\brb\b'), ('fco', r'l[ií]ngua azul.*pcr|pcr.*l[ií]ngua|btv|fco.*pcr|pcr.*fco')]
NOT_TEST = r'vacin|primo|rappel|s4|s8|dhe_|data_da'


def kind(h):
    h = str(h or '').lower()
    if re.search(NOT_TEST, h):
        return None
    for k, rx in TESTS:
        if re.search(rx, h):
            return k
    return None


def is_date_col(h):
    h = str(h or '').lower()
    return bool(re.search(r'colheita|dt\.? ?interven|data interven', h))


def res(v):
    s = str(v or '').strip().lower()
    if not s:
        return None
    if re.search(r'negativ|n[ãa]o detet|n[ãa]o detect|ausente', s):
        return 'N'
    if re.search(r'prejudic|inconclus|insufic|n[ãa]o realiz', s):
        return 'X'
    if re.search(r'positiv|detetado|detectado|duvid', s):
        return 'P'
    return '?'


def day(v):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', str(v or ''))
    return datetime.date(int(m[1]), int(m[2]), int(m[3])).isoformat() if m else None


def load(p):
    d = json.load(open(p, encoding='utf-8'))
    return d.get('data', d) if isinstance(d, dict) and 'data' in d and 'rows' not in d else d


A, fontes = {}, []


def add(sia, date, vals, fonte):
    if not date or not vals:
        return
    sid = str(sia).strip().upper()
    sid = sid[2:] if sid.startswith('PT') else sid
    rec = A.setdefault(sid, {}).setdefault(date, {'f': fonte})
    rec.update(vals)


# 1) importação principal (coleção animais + meta/import)
meta_p = os.path.join(src, 'meta', 'import.json')
if os.path.exists(meta_p):
    meta = load(meta_p)
    cols = meta.get('colunas', [])
    kinds = {i: kind(h) for i, h in enumerate(cols)}
    dcol = next((i for i, h in enumerate(cols) if is_date_col(h)), None)
    if any(kinds.values()) and dcol is not None:
        fi = len(fontes)
        fontes.append({'nome': meta.get('ficheiro', ''), 'importadoEm': meta.get('importadoEm', '')})
        n = 0
        for p in sorted(glob.glob(os.path.join(src, 'animais', '*.json'))):
            doc = load(p)
            if meta.get('importId') and doc.get('importId') not in (None, meta.get('importId')):
                continue
            for r in doc.get('rows', []):
                v = r.get('v', {})
                get = (lambda i: v.get(str(i))) if isinstance(v, dict) else (lambda i: v[i] if i < len(v) else None)
                vals = {k: res(get(i)) for i, k in kinds.items() if k and res(get(i))}
                add(r['s'], day(get(dcol)), vals, fi)
                n += 1
        fontes[fi]['n'] = n

# 2) ficheiros extra (resultados ACOS, etc.)
files = {}
for p in glob.glob(os.path.join(src, 'extras', '*.json')):
    d = load(p)
    files.setdefault(d.get('fid'), []).append(d)
for fid, parts in files.items():
    parts.sort(key=lambda d: d.get('n', 0))
    if len(parts) < parts[0].get('partes', 1):
        continue
    cols = parts[0].get('colunas', [])
    kinds = {i: kind(h) for i, h in enumerate(cols)}
    if not any(kinds.values()):
        continue
    dcol = next((i for i, h in enumerate(cols) if is_date_col(h)), None)
    info_date = next((day(v) for k, v in parts[0].get('info', []) if re.search(r'colheita', k, re.I)), None)
    fi = len(fontes)
    fontes.append({'nome': parts[0].get('nome', ''), 'importadoEm': parts[0].get('importadoEm', ''), 'n': 0})
    for d in parts:
        for r in d.get('rows', []):
            v = r.get('v', [])
            vals = {k: res(v[i]) for i, k in kinds.items() if k and i < len(v) and res(v[i])}
            add(r['s'], (day(v[dcol]) if dcol is not None and dcol < len(v) else None) or info_date, vals, fi)
            fontes[fi]['n'] += 1

ORDER = ['ibr', 'bvd', 'ehd', 'sbv', 'bru', 'fco']
out = {sid: [[d] + [r.get(k) for k in ORDER] + [r['f']] for d, r in sorted(dd.items())] for sid, dd in A.items()}
payload = {'gerado': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
           'ordem': ORDER, 'fontes': fontes, 'a': out}
with open(dst, 'w', encoding='utf-8') as f:
    f.write('window.ANALISES = ' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(f'{len(out)} animais com análises · fontes: ' + '; '.join(f"{x['nome']} ({x.get('n', 0)})" for x in fontes))
