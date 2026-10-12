# MELHORIAS — download_videos_youtube

> **Atualizado:** 2026-10-11 · Python 3.11–3.13 · GUI desktop · branch `master`
> **Escopo:** baixar um vídeo em MP4 com FreeSimpleGUI e pytubefix.

## 0. Como usar este documento

1. As prioridades seguem P0 → P1 → P2.
2. Os itens abaixo foram conferidos nos arquivos do projeto e atualizados após a implementação.
3. `download_teste_antigo.py` e `file.py` eram scripts de experimento, não usados pelo app; foram removidos por conterem comandos PowerShell e operações destrutivas.
4. **TEST-01 continua pendente.** Não foram criados nem executados testes automatizados nesta rodada.

## 1. Diagnóstico executivo

O app abria uma janela mínima, mas o primeiro clique falhava porque `os` não era
importado. O programa dependia de PowerShell, apagava sempre `1.mp4`, tratava erros da
rede como traceback e declarava três bibliotecas sem versão — inclusive FFmpeg que não
era usado. O README também recomendava Docker sem haver arquivos Docker.

A aplicação agora valida URLs, mantém a interface responsiva durante o download,
mostra progresso, permite escolher uma pasta e cancelar com segurança. Os arquivos são
salvos como MP4 com nome higienizado e o ID do vídeo. A GUI e o downloader estão fixados
em versões publicadas no PyPI; os experimentos obsoletos foram removidos.

## 2. Tabela de prioridades

| ID | Item | Severidade | Estado |
|---|---|---:|---|
| BUG-01 | Aplicativo falhava por `os` não importado | P0 | Implementado |
| BUG-02 | Dependência de PowerShell e caminho Windows | P0 | Implementado |
| SEC-01 | Dependências sem pin e pytube desatualizado | P1 | Implementado |
| BUG-03 | URL inválida e falhas sem tratamento amigável | P1 | Implementado |
| SEC-03 | Controles invisíveis/bidirecionais em títulos remotos | P1 | Implementado |
| DOC-01 | README recomendava Docker inexistente | P1 | Implementado |
| SEC-02 | Comandos de shell nos scripts legados | P2 | Implementado; scripts removidos |
| TEST-01 | Ausência de testes automatizados | P2 | Pendente |
| DEVOPS-01 | Ausência de CI | P2 | Implementado; workflow remoto verde em `5f774cb` |

## 3. Segurança

### SEC-01 · Dependências sem versão fixa · [P1]

- **Arquivo:** `requirements.txt`
- **Evidência:** `pytube` não recebia atualização desde 2023 e as três linhas de dependência não tinham versões; `ffmpeg-python` não era usado.
- **Mudança:** trocar para `pytubefix==11.2.0`, fixar `FreeSimpleGUI==5.3.0.post1` e remover a dependência FFmpeg sem uso.
- **Aceite:** instalação reproduzível com as duas bibliotecas efetivamente usadas pelo app.
- **Verificação:** `python -m pip install --dry-run -r requirements.txt`

### SEC-02 · Comandos PowerShell montados como texto · [P2]

- **Arquivo:** `download_teste_antigo.py`, `file.py`
- **Evidência:** os scripts antigos chamavam `os.system`, tentavam alterar o PATH e removiam/renomeavam arquivos com nomes fixos.
- **Mudança:** remover os dois experimentos sem uso; o aplicativo principal não executa comandos de shell.
- **Aceite:** nenhum script Python contém `os.system`, PowerShell, `setx` ou instalação de pacote em runtime.
- **Verificação:** `rg -n 'os\.system|powershell|setx|pip install' --glob '*.py' .`

### SEC-03 · Controles no título usado como nome de arquivo · [P1]

- **Arquivo:** `download_video_youtube.py`, `build_output_path`
- **Evidência:** o título vem da resposta remota e era incorporado ao nome. A filtragem removia C0, mas preservava C1, controles bidi e caracteres invisíveis que podem inverter ou confundir a exibição do nome.
- **Mudança:** substituir controles C0/C1, marcas direcionais e caracteres de isolamento bidi por `_` antes de formar o caminho.
- **Aceite:** o ID ainda distingue o vídeo e controles invisíveis não mudam a apresentação do nome no sistema de arquivos.
- **Verificação estática:** `rg -n 'build_output_path|x7f-\x9f|u202a-\u202e' download_video_youtube.py`

## 4. Bugs e defeitos funcionais

### BUG-01 · Falha por `os` não importado · [P0]

- **Arquivo:** `download_video_youtube.py`
- **Evidência:** o programa usava `os.path` sem importar `os` e encerrava ao iniciar um download.
- **Mudança:** substituir o fluxo incompleto por funções explícitas de validação, download e interface; o app não precisa de `os`.
- **Aceite:** o arquivo compila e não há referência a `os.path` sem import.
- **Verificação:** `python -m py_compile download_video_youtube.py`

### BUG-02 · Dependência de Windows/PowerShell · [P0]

- **Arquivo:** `download_video_youtube.py`
- **Evidência:** a criação do PATH chamava PowerShell e esperava `c:\FFMPEG\bin` mesmo sem usar o FFmpeg.
- **Mudança:** remover essa lógica e o código morto de conversão; o app salva MP4 e não exige FFmpeg.
- **Aceite:** nenhum caminho, executável ou comando específico de Windows permanece no app.
- **Verificação:** `rg -ni 'powershell|FFMPEG|\.exe|subprocess|getoutput' download_video_youtube.py`

### BUG-03 · URL e falhas não eram tratadas · [P1]

- **Arquivo:** `download_video_youtube.py`
- **Evidência:** qualquer texto era passado ao pytube; erros de URL, conexão ou download encerravam a interface com traceback.
- **Mudança:** aceitar somente hosts/IDs de vídeo válidos, canonicalizar em HTTPS, exibir erros em português e executar o download em thread com progresso e cancelamento.
- **Aceite:** URL inválida é recusada antes da rede; a janela continua responsiva e os erros são informados ao usuário.
- **Verificação:** `rg -n 'normalize_video_url|popup_error|ProgressBar|interrupt_checker' download_video_youtube.py`

## 5. Qualidade: testes

### TEST-01 · Ausência de testes automatizados · [P2]

- **Arquivo:** *(a criar)* `tests/`
- **Evidência:** não há suíte para validação de URL, nomes de saída ou cancelamento.
- **Mudança:** criar testes unitários offline para URLs válidas/inválidas, nomes seguros e interrupção, sem chamar o YouTube.
- **Aceite:** a suíte roda sem janela gráfica, rede ou credenciais.
- **Estado:** pendente; não foram adicionados nem executados testes nesta rodada.
- **Verificação futura:** `python -m pytest -q`

## 6. DevOps / Infra

### DEVOPS-01 · Verificações automáticas ausentes · [P2]

- **Arquivo:** `.github/workflows/ci.yml`, `requirements-dev.txt`, `pyproject.toml`
- **Evidência:** não havia CI ou configuração de lint.
- **Mudança:** adicionar workflow em push/PR para compilar o app e executar Ruff; inclui instalação reproduzível das dependências.
- **Aceite:** workflow versionado e execução remota verde; incluir `pytest` quando TEST-01 for implementado.
- **Verificação local:** `python -m py_compile download_video_youtube.py && ruff check download_video_youtube.py`
- **Estado:** workflow commitado e publicado; execução `CI` no commit `5f774cb` concluída com sucesso. O workflow só executa sintaxe e Ruff; testes seguem pendentes.

### DEVOPS-02 · Python 3.10 sem suporte e CI em uma versão · [P1]

- **Arquivos:** `README.md`, `pyproject.toml`, `.github/workflows/ci.yml`
- **Evidência:** Python 3.10 encerrou o suporte em 2026-10-01; o README declarava compatibilidade desde 3.10 e o workflow só verificava 3.13 em `ubuntu-latest`.
- **Mudança:** elevar o mínimo para 3.11, alinhar Ruff a `py311`, fixar Ubuntu 24.04 e executar os checks em Python 3.11 e 3.13, versões cobertas pelos classificadores do FreeSimpleGUI fixado.
- **Referência:** [Python 3.10.22 chegou ao fim de vida em 2026-10-01](https://www.python.org/downloads/release/python-31022/); [FreeSimpleGUI 5.3.0.post1 declara suporte até Python 3.13](https://pypi.org/project/FreeSimpleGUI/5.3.0.post1/).
- **Validação:** CI estática confirmará as duas versões depois do push; não adicionar nem executar testes.

## 7. Documentação

### DOC-01 · README incompatível com o projeto · [P1]

- **Arquivo:** `README.md`
- **Evidência:** recomendava Docker inexistente, descrevia downloads/FFmpeg que o app não fazia e ensinava a instalar uma dependência sem versão.
- **Mudança:** documentar Python/Tk, ambiente virtual, instalação, escolha da pasta, cancelamento e saída MP4; retirar Docker e conversão.
- **Aceite:** os comandos documentados correspondem aos arquivos e funções existentes.
- **Verificação:** `if rg -ni 'docker compose up|Dockerfile|conversão automática' README.md; then exit 1; else echo 'README sem instruções Docker obsoletas'; fi`

## 8. Ordem de execução

1. **Onda 0 — P0:** BUG-01 e BUG-02.
2. **Onda 1 — P1:** SEC-01, BUG-03 e DOC-01.
3. **Onda 2 — P2:** SEC-02, TEST-01 e DEVOPS-01.

As correções de código e documentação estão implementadas. TEST-01 permanece pendente;
a execução hospedada do workflow estática concluiu com sucesso no commit `5f774cb`.

## 9. Fora de escopo e riscos

- O aplicativo baixa um vídeo por vez e preserva o formato MP4 original.
- Não há extração de áudio, conversão, playlist, login OAuth ou download paralelo.
- A interface depende de Tcl/Tk e de uma sessão gráfica; o CI faz checagens estáticas.
- Baixe somente conteúdo cuja gravação você esteja autorizado a fazer.

## 10. Definição de pronto

- [x] BUG-01 — inicialização sem referência não importada.
- [x] BUG-02 — removidos PowerShell, caminho Windows e dependência de FFmpeg.
- [x] SEC-01 — dependências fixadas e pacote de download atualizado.
- [x] BUG-03 — URLs validadas, erros apresentados na interface e download cancelável.
- [x] SEC-03 — controles C0/C1 e bidirecionais removidos dos nomes.
- [x] SEC-02 — scripts legados com shell removidos.
- [ ] TEST-01 — suíte offline pendente.
- [x] DEVOPS-01 — arquivo CI publicado e execução remota verde em `5f774cb`.
- [x] DEVOPS-02 — mínimo Python 3.11 e CI em duas versões suportadas.
- [x] DOC-01 — README atualizado para o comportamento real.
- [x] O arquivo atual compila; dois scripts legados sem uso foram removidos.

*Validações estáticas locais e CI remoto concluídos em 2026-10-11. Nenhum teste, login ou download real foi executado.*
