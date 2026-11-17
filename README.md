# Monte do Pasto · Master Allocation

Aplicação de alocação de animais por mercado, cliente e carga (Monte do Pasto). É uma página única (`index.html`) que funciona no browser, sem servidor. Os dados ficam na pasta `_controlo/`.

> **Atenção: dados confidenciais.** O repositório inclui dados do efetivo (N.º SIA, alocações, clientes, vendas, análises, origens).
> - Crie o repositório como **privado**.
> - No GitHub Pages, um site publicado é **público** para quem tiver o link, mesmo com repositório privado. A exceção é o **GitHub Enterprise Cloud**, onde a visibilidade das Pages pode ser "Private" (só membros da organização com sessão iniciada).
> - Sem Enterprise, use um alojamento com login (por exemplo Azure Static Web Apps com autenticação Microsoft 365, ou Cloudflare Pages + Cloudflare Access).
> - A página tem `noindex` e o `robots.txt` bloqueia motores de busca. Isto evita que apareça em pesquisas, mas **não** é proteção de acesso.

## Conteúdo

| Caminho | O que é |
|---|---|
| `index.html` | A app completa (inclui uma cópia dos dados como reserva) |
| `_controlo/dados_alocacao.js` | Efetivo do ficheiro de alocação mais recente |
| `_controlo/analises_marrocos.js` | Análises da 2.ª parte do protocolo de Marrocos |
| `_controlo/angus_certificados.js` | Angus certificados (e-Exploração) |
| `_controlo/origens.js` | Origem dos animais (e-Exploração) |
| `scripts/` | Scripts que geram os dados e `atualizar_github.ps1` |
| `assets/` | Ícones |
| `.nojekyll` | Necessário: sem ele o GitHub Pages ignora a pasta `_controlo` |

## Publicar no GitHub Pages

1. No GitHub: **New repository** → nome `monte-do-pasto-master-allocation` → **Private** → Create.
2. Envie os ficheiros desta pasta, de uma das duas formas:
   - **Pelo site:** "uploading an existing file" e arraste todo o conteúdo da pasta. Inclua `.nojekyll`; no Windows, os ficheiros começados por ponto podem estar ocultos.
   - **Com Git:**
     ```
     git init
     git add -A
     git commit -m "Master Allocation"
     git branch -M main
     git remote add origin https://github.com/<organização>/monte-do-pasto-master-allocation.git
     git push -u origin main
     ```
3. **Settings → Pages**:
   - Source: *Deploy from a branch*;
   - Branch: `main`, pasta `/ (root)` → Save;
   - em GitHub Enterprise, escolha também **Visibility: Private**.
4. Ao fim de 1–2 minutos o site fica em `https://<organização>.github.io/monte-do-pasto-master-allocation/`.

## Funcionalidades online e ligações

Tudo o que a app faz na versão da pasta partilhada funciona online: simulador, painel, alocações, programação de cargas, efetivo, calculadora e calendário, e exportações para Excel. Para as ligações aos ficheiros use **Chrome ou Edge**, que permitem ler pastas do computador.

| Ligação | Como funciona online |
|---|---|
| Ficheiro de alocação da Alexandra | **Escolher pasta**: escolha a pasta sincronizada `…\Alexandra Silva\2026 - Alocação de Animais`. A app lembra-se da pasta. **Atualizar com a versão mais recente** lê sempre o `Alocação…xlsx` mais recente. |
| Dados da verificação diária (análises Marrocos, Angus certificados, origens) | **Ligar pasta da app**: escolha a pasta sincronizada `App Alocação Animais`. A app passa a ler o `_controlo` atualizado todos os dias às 17h, sem precisar de publicar no GitHub. |
| Dados incluídos no site | Se nenhuma pasta estiver ligada (por exemplo, no telemóvel), usa os dados de `_controlo/` deste repositório. |
| Alocações bloqueadas, negócios, vendas marcadas à mão, datas de saída | Ficam guardados **no browser**. A versão online não vê o que foi feito na versão da pasta partilhada (são "sites" diferentes). Para passar de uma para a outra: no **Início**, *Guardar cópia (ficheiro)* numa e *Carregar cópia…* na outra. |

## Atualizar o site

A verificação diária das 17h atualiza a pasta partilhada, não o GitHub. Para publicar a versão mais recente da app e dos dados, abra o PowerShell na pasta do repositório clonado e corra:

```
.\scripts\atualizar_github.ps1
```

O script copia `App_Alocacao_Animais.html` para `index.html`, copia os ficheiros de `_controlo` e faz commit e push com as suas credenciais Git.
