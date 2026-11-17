"""Gera dados_alocacao.js (dados que a App de Alocação carrega ao abrir) a partir do ficheiro de alocação mais recente.

Uso: python3 gerar_dados.py <Alocação...xlsx> <saida.js> [mtimeMs]
Replica a leitura da app (folhas Dados e Quadro Alocações).
"""
import sys, re, json, datetime, os
import openpyxl

src, dst = sys.argv[1], sys.argv[2]
mtime = int(sys.argv[3]) if len(sys.argv) > 3 else int(os.path.getmtime(src) * 1000)
EPOCH = datetime.date(1970, 1, 1)


def day(v):
    if v is None or v == '':
        return -1
    if isinstance(v, datetime.datetime):
        return -1 if v.year < 2000 else (v.date() - EPOCH).days
    if isinstance(v, datetime.date):
        return -1 if v.year < 2000 else (v - EPOCH).days
    if isinstance(v, (int, float)):
        return round(v - 25569) if v > 30000 else -1
    s = str(v)
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        return (datetime.date(int(m[1]), int(m[2]), int(m[3])) - EPOCH).days
    m = re.search(r'(\d{2})[-/](\d{2})[-/](\d{4})', s)
    if m:
        return (datetime.date(int(m[3]), int(m[2]), int(m[1])) - EPOCH).days
    return -1


wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
ws = wb['Dados']
it = ws.iter_rows(values_only=True)
H = [('' if isinstance(h, (datetime.datetime, datetime.date)) or h is None else str(h).strip()) for h in next(it)]
ix = lambda n: H.index(n) if n in H else -1
need = ['ANIMAL', 'Data Nasc.', 'Grupo', 'Alocação', 'Sexo', 'Ult Peso', 'Data Ult Peso', 'Nome']
miss = [n for n in need if ix(n) < 0]
if miss:
    sys.exit('Faltam colunas na folha Dados: ' + ', '.join(miss))
c = dict(id=ix('ANIMAL'), b=ix('Data Nasc.'), g=ix('Grupo'), a=ix('Alocação'), s=ix('Sexo'), w=ix('Ult Peso'), wd=ix('Data Ult Peso'),
         nome=ix('Nome'), qe=ix('Quarentena Explo.'), dest=ix('Destino - E.exploração'), farm=ix('Marca'), breed=ix('Raça'),
         fco=ix('Primo_S8'), dhe=ix('Primo_DHE'), gmd=ix('GMD'), dofs=ix('DOFS'), pont=ix('Pontuação'))
pat = re.compile(r'coabit|risco|observa|enferm', re.I)
A, F, R, G, N = [], [], [], [], []
def idx(lst, v):
    if v not in lst:
        lst.append(v)
    return lst.index(v)
get = lambda row, i: row[i] if 0 <= i < len(row) else None
def txt(v):
    if v is None or isinstance(v, datetime.time):
        return ''
    return str(v)
rows = []
for row in it:
    sid = get(row, c['id'])
    if not isinstance(sid, str) or not sid.upper().startswith('PT'):
        continue
    nome = txt(get(row, c['nome'])).strip()
    av = get(row, c['a'])
    alloc = '(sem alocação)' if av is None or av == 0 or isinstance(av, datetime.time) else str(av)
    qm = re.search(r'quarentena\s*(\d{4}-\d{2}-\d{2})', nome, re.I)
    q = day(qm[1]) if qm else (-1 if nome in ('', '0') else -2)
    fields = [nome, alloc, txt(get(row, c['qe'])), txt(get(row, c['g']))]
    ex = 2 if any(pat.search(x) for x in fields) or re.search(r'coabit|risco', txt(get(row, c['dest'])), re.I) else 0
    try:
        w = float(get(row, c['w']) or 0)
    except (TypeError, ValueError):
        w = 0
    num = lambda v: float(v) if isinstance(v, (int, float)) else None
    gmd, dofs = num(get(row, c['gmd'])), num(get(row, c['dofs']))
    rows.append([sid[2:], 1 if txt(get(row, c['s'])).upper() == 'M' else 0, day(get(row, c['b'])), round(w, 1), day(get(row, c['wd'])), q, ex,
                 day(get(row, c['fco'])), idx(A, alloc), idx(F, txt(get(row, c['farm'])) or '?'), idx(R, txt(get(row, c['breed'])) or '?'),
                 idx(G, txt(get(row, c['g'])) or '?'), -1, day(get(row, c['dhe'])),
                 None if gmd is None else round(gmd, 3), None if dofs is None else int(dofs),
                 1 if re.search(r'angus\s*certificad', nome, re.I) else 0, -1 if (qm or not nome or nome == '0') else idx(N, nome),
                 int(get(row, c['pont'])) if isinstance(get(row, c['pont']), (int, float)) else None])

green, qsec = [], []
if 'Quadro Alocações' in wb.sheetnames:
    vals = [r[0] for r in wb['Quadro Alocações'].iter_rows(min_col=1, max_col=1, values_only=True)]
    vals = [str(v).strip() for v in vals if isinstance(v, str) and v.strip()]
    for s in vals:
        if re.match(r'total exporta', s, re.I):
            break
        if not re.match(r'total', s, re.I):
            green.append(s)
    sec, seen = 'Exportação', set()
    for s in vals:
        if re.match(r'total exporta', s, re.I): sec = 'Angus'; continue
        if re.match(r'total angus', s, re.I): sec = 'Mercado Nacional – Carne'; continue
        if re.match(r'total mercado nacional', s, re.I): sec = 'Mercado – Carcaças / Espanha'; continue
        if re.match(r'total mercado.*(carca|espanh)', s, re.I): sec = 'Outros'; continue
        if re.match(r'total', s, re.I): continue
        if s not in seen:
            seen.add(s); qsec.append([s, sec])

out = dict(src=os.path.basename(src), mtime=mtime, gerado=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
           A=A, F=F, R=R, G=G, N=N, rows=rows, GREEN=green, QSEC=qsec)
with open(dst, 'w', encoding='utf-8') as f:
    f.write('window.DADOS_ALOCACAO = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(f"{len(rows)} animais · {os.path.basename(src)} · alterado {datetime.datetime.fromtimestamp(mtime/1000):%d-%m-%Y %H:%M}")
