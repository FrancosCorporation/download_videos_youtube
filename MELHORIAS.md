# MELHORIAS — download_videos_youtube

> **Gerado por análise de código em 2026-10-05** · Stack: Python 3 + PySimpleGUI + pytube (GUI desktop)
> Branch `main` · 3 arquivos `.py` (`download_video_youtube.py` 33 linhas, `download_teste_antigo.py` 50, `file.py` 7) · **0 suite(s) de teste** · sem CI · sem Dockerfile
>
> **Este arquivo é um plano de execução.** Cada item tem ID, `arquivo:linha`, mudança exata,
> critério de aceite e comando de verificação.

---

## 0. Como usar este documento

1. Execute na ordem **P0 → P1 → P2**, respeitando as ondas da seção 8.
2. Ao terminar um item: marque `- [x]`, rode o comando do campo **Verificação**, comite `fix(<ID>): descrição`.
3. **O script principal é `download_video_youtube.py`.** `download_teste_antigo.py` é legado e `file.py` é um utilitário de PATH — quando a mudança mexer no padrão PowerShell/PATH, aplique nos três arquivos.
4. Todo `arquivo:linha` deste documento veio da leitura direta do repositório; não troque uma referência sem reler o arquivo.
5. **Idioma:** português.

---

## 1. Diagnóstico executivo

App de desktop para baixar vídeos do YouTube: o PySimpleGUI abre uma janela com um campo de URL, o pytube baixa na maior resolução e uma segunda janela confirma o fim. O repositório é mínimo: `download_video_youtube.py` (33 linhas, principal), `download_teste_antigo.py` (50, legado), `file.py` (7, utilitário de PATH), `requirements.txt` (`pytube`, `pysimplegui`, `ffmpeg-python` — **sem nenhuma versão pinada**), além de `README.md`, `LICENSE` e `.gitignore`. Zero testes, zero CI e um README que promove Docker inexistente.

**O que está bem:**

| Item | Evidência |
|---|---|
| Projeto mínimo e legível | 3 scripts curtos: `download_video_youtube.py` (33 linhas), `download_teste_antigo.py` (50), `file.py` (7) |
| Dependências declaradas | `requirements.txt` lista as libs da GUI: `pytube`, `pysimplegui`, `ffmpeg-python` |
| Fluxo de UI simples | janela de URL → download → janela "Concluido !!", com Cancel/fechar encerrando via `sys.exit()` |
| Repositório limpo | `git ls-files` mostra apenas `.gitignore`, `LICENSE`, `README.md`, 3 `.py` e `requirements.txt` |

**O que está quebrado:**

| Item | Evidência |
|---|---|
| **BUG-01** — o script principal crasha ao abrir | usa `os.path` (linhas 19, 20) mas **nunca** faz `import os` → `NameError` em runtime (`py_compile` não pega) |
| **BUG-02** — amarrado a Windows/PowerShell | `powershell "$env:PATH"` (linha 7) + `powershell ./ffmpeg/bin/ffmpeg.exe` (linha 28, em comentário, mas o pattern vive) |
| **SEC-01** — dependências sem pin | `requirements.txt` sem `==`; `pysimplegui` foi descontinuado (migrou para `FreeSimpleGUI`) |
| **BUG-03** — URL sem validação | `YouTube(values[0])` direto no texto digitado → exceção não tratada (traceback cru na GUI) |
| **SEC-02** — comando por string | `os.system` com f-string (`download_video_youtube.py:28`) e `pip install` via powershell (`download_teste_antigo.py:6`) |
| **DOC-01** — o README mente | descreve `docker compose up --build`, mas não há Dockerfile nem compose em `git ls-files` |
| Sem testes e sem CI | **TEST-01** e **DEVOPS-01**: nada roda automaticamente |
| `ffmpeg-python` declarado mas não usado | o código chama `subprocess.getoutput('powershell ...')` em vez da lib |

---

## 2. Tabela de prioridades

| ID | Título | Sev | Arquivo | Depende de |
|---|---|---|---|---|
| BUG-01 | `os` sem `import os` — crash `NameError` ao abrir | **P0** | `download_video_youtube.py:19-20` | — |
| BUG-02 | PowerShell/caminho Windows hardcoded | **P0** | `download_video_youtube.py:7` | — |
| SEC-01 | Deps sem pin + `pysimplegui` descontinuado | **P1** | `requirements.txt` | — |
| BUG-03 | URL sem validação; exceção não tratada | **P1** | `download_video_youtube.py` | — |
| DOC-01 | README promove Docker inexistente | **P1** | `README.md` | BUG-02 |
| SEC-02 | `os.system` com f-string (comando por string) | **P2** | `download_video_youtube.py:28` | — |
| TEST-01 | Zero testes | **P2** | *(ausente)* | BUG-01, BUG-03 |
| DEVOPS-01 | Sem CI | **P2** | *(ausente)* | TEST-01 |

**Placar: 2 P0 · 3 P1 · 3 P2 · 0 P3 = 8 itens.**

---

## 3. Segurança

### SEC-01 · Dependências sem pin e `pysimplegui` descontinuado · [P1]

- **Arquivo:** `requirements.txt`
- **Evidência:** o arquivo tem exatamente três linhas e **nenhuma traz versão**: `pytube`, `pysimplegui`, `ffmpeg-python`. `pytube` quebra com frequência por mudanças feitas pelo próprio YouTube; a lib `PySimpleGUI` migrou de `pysimplegui` para `FreeSimpleGUI` após mudança de licença. Ainda: `ffmpeg-python` é declarado mas o código **não** o importa — usa `subprocess.getoutput('powershell ...')`.
- **Impacto:** instalação não reproduzível e com risco real de falhar: hoje `pysimplegui` pode não instalar ou ser uma dependência não livre, amanhã um `pytube` novo quebra contra a API do YouTube. Quem clonar o repo não tem garantia nenhuma de conseguir rodar.
- **Mudança:** (1) rodar uma instalação limpa, anotar as versões que funcionam e pinar **todas** as linhas com `==`; (2) substituir `pysimplegui` por `FreeSimpleGUI` (fork livre) ajustando o import para `import FreeSimpleGUI as sg` — ou, se preferir manter o nome original, fixar explicitamente a última versão compatível e documentar a escolha; (3) **remover `ffmpeg-python`**, porque nada o importa (se um dia o `resize` voltar, aí sim reinstale e use de fato).
- **Aceite:** `grep -cE '==' requirements.txt` = 3; um venv novo instala do zero sem erro; `python3 -c "import <lib>"` passa para cada dependência pinada.
- **Verificação:**
  ```bash
  ! grep -qE '^[A-Za-z0-9_.-]+$' requirements.txt || { echo "FAIL: linha sem versão"; exit 1; }
  test "$(grep -cE '^[A-Za-z0-9_.-]+==[^ ]+$' requirements.txt)" -eq 3 && echo "OK: 3 deps pinadas"
  python3 -m venv /tmp/venv-melhorias
  /tmp/venv-melhorias/bin/pip install -q -r requirements.txt && echo "OK: instalação limpa"
  ```

### SEC-02 · `os.system` com f-string — comando executado por string · [P2]

- **Arquivo:** `download_video_youtube.py:28` e `download_teste_antigo.py:6`
- **Evidência:** no principal, a linha 28 executa `os.system(f''+ comando_ffmpeg .format(...))` dentro do comentário `resize` cujo template (`powershell ./ffmpeg/bin/ffmpeg.exe -i {input} ...`) está logo acima; no legado, `download_teste_antigo.py:6` roda `os.system(f'powershell "pip install -r requirements.txt"')` — e mais `os.system` aparecem no mesmo arquivo para `cp`, `setx path` e `ffmpeg`. Todos montam o comando como string e jogam no shell.
- **Impacto:** pattern inseguro por hábito: hoje os interpolantes são literals, mas basta um dia passar nome de arquivo vindo da entrada (ou da URL) para virar injeção de comando. Além disso, instalar dependências rodando `pip` dentro do script esconde falhas de instalação atrás de uma string.
- **Mudança:** eliminar todo `os.system` do repo; quando precisar chamar um programa externo, usar `subprocess.run([...lista de args...], shell=False, check=True, capture_output=True)` — nunca f-string de shell. Para dependências, tirar o `pip install` de dentro do código e orientar `python -m pip install -r requirements.txt` no README (ou em um passo de CI).
- **Aceite:** `grep -rn "os.system" --include='*.py' .` volta vazio; nenhum arquivo do repo monta comando por interpolação de string.
- **Verificação:**
  ```bash
  ! grep -rn --include='*.py' 'os.system' . || { echo "FAIL: os.system presente"; exit 1; }
  ! grep -rn --include='*.py' 'pip install -r' . || { echo "FAIL: pip rodando de dentro do código"; exit 1; }
  grep -rn --include='*.py' 'subprocess.run' . || echo "aviso: nenhum subprocess.run (ok se não houver chamada externa)"
  echo "OK: sem comando por string"
  ```

---

## 4. Bugs e defeitos funcionais

### BUG-01 · `os` usado sem `import os` — o script principal crasha ao abrir · [P0]

- **Arquivo:** `download_video_youtube.py:19-20` (com os imports no topo do mesmo arquivo)
- **Evidência:** as linhas 19 e 20 chamam `os.path.exists("1.mp4")` e `os.remove("1.mp4")`, mas o arquivo importa apenas `subprocess`, `sys`, `PySimpleGUI` e `pytube` (`from pytube import YouTube`) — `grep '^import'` **não mostra `os`**. `python3 -m py_compile download_video_youtube.py` passa sem reclamar, porque `NameError` só existe em tempo de execução.
- **Impacto:** ao clicar "Ok" com qualquer URL, o processo aborta com `NameError: name 'os' is not defined` antes mesmo de chamar o pytube — o download nunca acontece e o usuário só vê um traceback cru no terminal. É o defeito que impede o app de funcionar hoje.
- **Mudança:** adicionar `import os` no topo, junto dos demais imports:
  ```python
  import os
  import subprocess
  import sys
  import PySimpleGUI as sg
  from pytube import YouTube
  ```
  Depois rode a **Verificação** completa: só `py_compile` continua verde com o defeito presente.
- **Aceite:** `os` consta entre os módulos importados (check AST abaixo) e clicar Ok com URL válida não levanta `NameError`.
- **Verificação:**
  ```bash
  grep -n '^import' download_video_youtube.py        # deve incluir `import os`
  python3 -m py_compile download_video_youtube.py
  python3 - <<'PY'
  import ast, pathlib
  tree = ast.parse(pathlib.Path("download_video_youtube.py").read_text())
  mods = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
  mods |= {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
  assert "os" in mods, "FAIL: os NAO importado"
  print("OK: os importado")
  PY
  ```

### BUG-02 · Caminho Windows/PowerShell hardcoded — não roda em Linux · [P0]

- **Arquivo:** `download_video_youtube.py:7` e o comentário na linha 28 (mesmo padrão em `file.py`, o utilitário de PATH)
- **Evidência:** a linha 7 monta o PATH através do shell do Windows:
  ```python
  path = subprocess.getoutput(f'powershell "$env:PATH"')+";c:\\FFMPEG\\bin;"
  ```
  e o template `powershell ./ffmpeg/bin/ffmpeg.exe -i {input} ...` aparece no comentário `resize` (linha 28) — em comentário, mas o pattern vive no código (e o `path.replace('"', "")` logo na linha seguinte sequer guarda o resultado). O README, ao mesmo tempo, promove Docker — GUI com PowerShell não convive com container Linux.
- **Impacto:** fora de um Windows com FFmpeg em `c:\FFMPEG\bin`, tudo falha: em Linux o comando `powershell` não existe, `getoutput` devolve erro do shell e o PATH fica errado. Dupla inconsistência: o README manda rodar em Docker (Linux) enquanto o código só conhece Windows.
- **Mudança:** montar PATH com recursos nativos — ler `os.environ["PATH"]`, anexar diretórios com `os.pathsep` (nunca `;` fixo) e resolver o binário com `shutil.which("ffmpeg")`; apagar todo `powershell`, `c:\FFMPEG\bin` e `.exe` de `download_video_youtube.py` e `file.py`. Se o `resize` for mantido, executar `subprocess.run([ffmpeg, "-i", entrada, ...], shell=False)`; se não, remover o bloco morto. O binário passa a vir do sistema (`apt install ffmpeg` / `brew install ffmpeg`), não de caminho hardcoded.
- **Aceite:** grep por `powershell`, `FFMPEG` e `.exe` volta vazio nos `.py`; em máquina Linux com ffmpeg no PATH, o script abre e chega ao download sem erro de shell.
- **Verificação:**
  ```bash
  ! grep -niE 'powershell|\.exe' download_video_youtube.py file.py || { echo "FAIL: padrão Windows"; exit 1; }
  ! grep -n 'FFMPEG' download_video_youtube.py file.py || { echo "FAIL: caminho hardcoded"; exit 1; }
  grep -nE 'os\.environ|os\.pathsep|shutil\.which' download_video_youtube.py   # caminho nativo presente
  command -v ffmpeg >/dev/null && echo "OK: ffmpeg resolvível pelo PATH do sistema"
  ```

### BUG-03 · URL sem validação e exceção não tratada na GUI · [P1]

- **Arquivo:** `download_video_youtube.py` (ramo `else`, logo após `window.close()` — a chamada `youtube = YouTube(values[0])`)
- **Evidência:** o texto digitado vai direto para `YouTube(values[0])` sem nenhuma checagem de formato e sem `try/except`: URL vazia, colada errada ou não-YouTube levanta exceção do pytube e o traceback sobe cru no lugar da interface. No mesmo arquivo, `subprocess.getoutput` (linha 7) roda comando através de shell sem necessidade.
- **Impacto:** qualquer erro comum de digitação quebra a experiência (traceback em vez de mensagem), a janela "Concluido !!" nunca aparece e o usuário não sabe se o problema é a URL, a rede ou o app. O shell desnecessário amplia a superfície de ataque e já é corrigido junto com BUG-02.
- **Mudança:** (1) validar antes de instanciar: regex que aceite apenas `https://www.youtube.com/watch?v=...` e `https://youtu.be/...`, e nesse caso `sg.popup_error("URL inválida")` + voltar para a janela; (2) envolver `YouTube(...)` e o `.download()` em `try/except Exception as e` com `sg.popup_error(f"Falha no download: {e}")` — nunca traceback cru; (3) trocar `subprocess.getoutput` por `subprocess.run([...], capture_output=True, text=True)` com `shell=False` (ou remover a chamada junto com BUG-02).
- **Aceite:** URL vazia/lixo mostra popup e o processo segue vivo; URL válida baixa normalmente; nenhuma chamada `getoutput` restante.
- **Verificação:**
  ```bash
  grep -nE 'youtu\.be|youtube\.com/watch' download_video_youtube.py    # validação presente
  grep -nE 'except|popup_error' download_video_youtube.py              # tratamento amigável presente
  ! grep -n 'getoutput' download_video_youtube.py || { echo "FAIL: shell desnecessário"; exit 1; }
  echo "OK: URL validada e erros tratados"
  ```

---

## 5. Qualidade: testes

### TEST-01 · Zero testes automatizados · [P2]

- **Arquivo:** *(ausente)* — não existe diretório ou arquivo de teste (`git ls-files` mostra só `.gitignore`, `LICENSE`, `README.md`, 3 `.py` e `requirements.txt`)
- **Evidência:** nenhum arquivo de teste no repo, `pytest` fora do `requirements.txt` e nenhuma suíte mencionada. O defeito BUG-01 — `NameError` no primeiro clique — passaria despercebido por qualquer suite mínima.
- **Impacto:** a única "verificação" atual é abrir a GUI e clicar; regressões como imports faltantes, quebra do pytube contra a API do YouTube ou mudança de nome da lib de GUI só aparecem quando alguém roda o app na mão.
- **Mudança:** criar `tests/` com `pytest` cobrindo, no mínimo: (1) checagem estática (AST) de que o script principal importa tudo que usa — pega BUG-01; (2) função de validação de URL extraída como função pura e testada com entradas válidas/inválidas — pega BUG-03; (3) helper de PATH portável sem `powershell` — pega BUG-02. Separe a lógica de GUI em funções para não precisar abrir janela nos testes.
- **Aceite:** `python3 -m pytest -q` passa com ao menos uma suíte, local e no CI (DEVOPS-01).
- **Verificação:**
  ```bash
  python3 -m pip install -q pytest
  python3 -m pytest -q                          # deve passar
  ls tests/                                      # suíte existe no repo
  ```

---

## 6. DevOps / Infra

### DEVOPS-01 · Sem integração contínua · [P2]

- **Arquivo:** *(ausente)* — nenhum workflow de CI em `git ls-files`
- **Evidência:** o repo não tem `.github/workflows/` (nem outra configuração de CI) e também não tem Dockerfile — o README só promove um Docker inexistente (ver DOC-01). Nada roda sozinho em push ou PR.
- **Impacto:** testes, instalação de dependências e checagens dependem de alguém lembrar de rodar; BUG-01 e a instalação quebrada de SEC-01 teriam sido flagrados por um job mínimo de CI no primeiro push.
- **Mudança:** adicionar GitHub Actions: em push/PR para a branch principal, usar `actions/setup-python`, rodar `python -m pip install -r requirements.txt`, `python3 -m py_compile` nos `.py` e `pytest -q`. Depois que TEST-01 existir, o mesmo job passa a ser a porta de entrada obrigatória.
- **Aceite:** o workflow existe, dispara em push/PR e aparece verde na última execução.
- **Verificação:**
  ```bash
  git ls-files | grep -E '^\.github/workflows/.+\.(yml|yaml)$'   # workflow versionado
  python3 -m py_compile download_video_youtube.py file.py        # mesmo gate de sintaxe do CI
  ```

---

## 7. Documentação

### DOC-01 · README descreve Docker que não existe no repositório · [P1]

- **Arquivo:** `README.md`
- **Evidência:** o README instrui `docker compose up --build` e menciona Dockerfile/docker-compose, mas `git ls-files` mostra apenas `.gitignore`, `LICENSE`, `README.md`, `download_teste_antigo.py`, `download_video_youtube.py`, `file.py` e `requirements.txt` — **não há Dockerfile nem docker-compose.yml**. Soma-se o conflito de BUG-02: mesmo que existissem, GUI + PowerShell não rodam em container Linux.
- **Impacto:** a primeira tentativa de qualquer pessoa falha justamente na linha de comando mais importante do README — instrução que não executa destrói a confiança no projeto inteiro e faz o leitor desistir antes de testar o app.
- **Mudança:** escolher uma verdade e executá-la: **(a) recomendado** — remover toda a seção Docker do README enquanto BUG-02 existir e documentar o que realmente funciona (Windows com FFmpeg, ou Linux após BUG-02); **(b)** criar `Dockerfile` + `docker-compose.yml` reais, testados em Linux. Nada de documentar o que não existe.
- **Aceite:** ou o README não cita mais Docker, ou cada comando documentado executa com sucesso a partir de um clone limpo.
- **Verificação:**
  ```bash
  if grep -qi 'docker' README.md; then
    ls -l Dockerfile docker-compose.yml 2>/dev/null || { echo "FAIL: README fala de Docker sem os arquivos"; exit 1; }
    echo "README e repo batem (Docker existe)"
  else
    echo "OK: README sem menção a Docker"
  fi
  ```

---

## 8. Ordem de execução (waves)

Execute nesta ordem; cada onda fecha com suas verificações verdes.

**Onda 0 — P0 (o app não roda sem isso)**

1. **BUG-01** — adicionar `import os` (correção mínima; destrava o script).
2. **BUG-02** — remover PowerShell/caminho Windows; PATH nativo + `shutil.which` em `download_video_youtube.py` e `file.py`.

**Onda 1 — P1 (instalação, robustez e verdade do README)**

3. **SEC-01** — pinar `requirements.txt`, migrar `pysimplegui` → `FreeSimpleGUI`, remover `ffmpeg-python` não usado.
4. **BUG-03** — validar URL, `try/except` com popup e fim do `subprocess.getoutput`.
5. **DOC-01** — deixar o README honesto (a decisão sobre Docker só depois de BUG-02 resolvido).

**Onda 2 — P2 (qualidade e automação)**

6. **SEC-02** — eliminar `os.system` dos três `.py` e o `pip install` de dentro do código.
7. **TEST-01** — suíte `pytest` cobrindo os defeitos das ondas 0-1.
8. **DEVOPS-01** — CI rodando `py_compile` + `pytest` em todo push (depois de TEST-01).

---

## 9. Fora de escopo / riscos

- **Reescrever a GUI** (trocar PySimpleGUI por Tkinter/Qt/web) está fora de escopo — só a migração mínima `pysimplegui` → `FreeSimpleGUI` exigida por SEC-01.
- **`download_teste_antigo.py` é legado**: opção válida é arquivar/removê-lo em vez de corrigi-lo; se mantiver, SEC-02 e BUG-02 valem para ele também.
- **`file.py`** (utilitário de PATH, 7 linhas) pode morrer junto com BUG-02 em vez de ser migrado.
- **Pin não é garantia eterna**: mesmo pinado, `pytube` pode quebrar quando o YouTube mudar do lado de lá — manter rotina de atualização (o CI de DEVOPS-01 ajuda a flagrar).
- **ffmpeg hoje é promessa morta**: `ffmpeg-python` está no requirements mas nada o importa; não criar função de transcodificação só para justificar a dependência — decidir usar de fato ou remover (SEC-01).
- **Docker só depois de BUG-02**: container Linux exige GUI sem PowerShell; expor a janela via X11/VNC está fora do que este plano promete.
- **Este plano não muda o comportamento do download** além de corrigir defeitos: mesma janela, mesma resolução máxima, mesmo fluxo.

---

## 10. Definição de pronto (DoD)

O plano só está pronto quando **todos** os itens abaixo forem verdadeiros:

- [ ] **BUG-01:** `import os` presente e o script não aborta com `NameError` ao clicar Ok.
- [ ] **BUG-02:** grep por `powershell`/`FFMPEG`/`.exe` vazio nos `.py`; PATH montado com `os.environ` + `os.pathsep` e ffmpeg via `shutil.which`.
- [ ] **SEC-01:** `requirements.txt` com as 3 linhas pinadas (`==`), lib de GUI definida (`FreeSimpleGUI` ou PySimpleGUI fixado) e `ffmpeg-python` removido; venv novo instala limpo.
- [ ] **BUG-03:** URL inválida gera `popup_error` e não traceback; sem `subprocess.getoutput`.
- [ ] **SEC-02:** `grep -rn 'os.system' --include='*.py' .` vazio; sem `pip install` dentro do código.
- [ ] **DOC-01:** README não cita Docker inexistente (ou o Dockerfile/compose existe e sobe).
- [ ] **TEST-01:** `python3 -m pytest -q` verde com ao menos 1 suíte.
- [ ] **DEVOPS-01:** workflow de CI versionado e verde no último push.
- [ ] `python3 -m py_compile` dos três `.py` passa e `python3 /tmp/validate.py download_videos_youtube` continua **OK**.

---

*Fim do plano. Gerado por leitura direta do código em 2026-10-05. Nenhum item já estava corrigido — todos apontam para defeitos ainda presentes.*