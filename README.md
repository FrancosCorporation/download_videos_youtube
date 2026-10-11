# Baixar vídeos do YouTube

Aplicativo desktop para baixar um vídeo público em MP4. A janela mostra o andamento,
permite escolher a pasta de destino e aceita links `youtube.com/watch` e `youtu.be`.
Cada arquivo recebe um nome seguro com o título e o ID do vídeo; downloads anteriores
não são sobrescritos.

## Requisitos

- Python 3.10 a 3.13.
- Tcl/Tk disponível no Python para abrir a interface. No Ubuntu/Debian, instale-o com
  `sudo apt install python3-tk`.
- Uma interface gráfica ativa. Este aplicativo não funciona em um terminal sem desktop.

O programa salva apenas o MP4 original. Não precisa de FFmpeg nem converte para MP3.

## Instalação e uso

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate       # Windows PowerShell
python -m pip install -r requirements.txt
python download_video_youtube.py
```

Na janela, cole a URL de um vídeo, escolha onde salvar e clique em **Baixar vídeo**.
O botão de cancelamento interrompe o download; fechar a janela durante o processo também
solicita o cancelamento.

## Verificações de desenvolvimento

```bash
python -m pip install -r requirements-dev.txt
python -m py_compile download_video_youtube.py
ruff check download_video_youtube.py
```

O workflow de CI executa a compilação sintática e o Ruff. O projeto ainda não tem uma
suíte de testes automatizados.

## Uso responsável

Baixe somente conteúdo que você tem autorização para salvar. Consulte os
[Termos de Serviço do YouTube](https://www.youtube.com/t/terms).

## Licença

MIT — consulte [LICENSE](LICENSE).
