"""Gera angus_certificados.js a partir da lista tirada do e-Exploração.
Uso: python3 gerar_certificados.py <lista.txt> <saida.js>
lista.txt: entradas "SIA9:NUM" separadas por vírgulas ou linhas (SIA sem 'PT'; NUM = n.º do certificado, pode vir vazio;
sufixo S quando o Nome diz SONAE). Ex.: 035763079:13932S,035915034:14046
"""
import sys, json, datetime, re
items = [x.strip() for x in re.split(r'[,\n]+', open(sys.argv[1], encoding='utf-8').read()) if x.strip()]
a = {}
for it in items:
    s, _, n = it.partition(':')
    s = re.sub(r'\D', '', s)[-9:]
    if len(s) != 9:
        continue
    a[s] = [n.rstrip('Ss'), 1 if n.upper().endswith('S') else 0]
out = {'gerado': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
       'fonte': 'e-Exploração · Relatório Configurável (N.º SIA, Nome) · animais presentes', 'a': a}
open(sys.argv[2], 'w', encoding='utf-8').write('window.ANGUS_CERT = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(f'{len(a)} animais com "Angus certificados" no Nome')
