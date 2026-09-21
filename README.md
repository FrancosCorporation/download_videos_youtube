# Download de Vídeos do YouTube

## 🐳 Instalação e Execução (Docker) — recomendado

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) + Docker Compose

### Rodar com Docker
```bash
docker compose up --build
```
O app é desktop/GUI — o container não é o fluxo recomendado. Use local.

### Sem Docker (local)
```bash
pip install -r requirements.txt
python download_video_youtube.py
```
App desktop (PySimpleGUI) — Windows/Linux com interface gráfica.

Ferramenta desktop (Windows) com interface gráfica para baixar vídeos e
playlists do YouTube, convertendo automaticamente para MP3/MP4 com **FFmpeg**.

![Python](https://img.shields.io/badge/Python-3-3776AB?style=flat-square&logo=python&logoColor=white)
![PySimpleGUI](https://img.shields.io/badge/GUI-PySimpleGUI-blue?style=flat-square)
![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=flat-square&logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/status-estudo%20(2022)-lightgrey?style=flat-square)

## Sobre

Script de estudo de 2022 que virou uma pequena ferramenta de uso pessoal:
abre uma janela (PySimpleGUI) onde você cola a URL do vídeo ou playlist, e o
download é feito com **pytube** com o apoio do **FFmpeg** para conversão.

## Funcionalidades

Comprovadas pelo código em `download_video_youtube.py`:

- Janela com campo de URL e botões Ok/Cancelar (`PySimpleGUI`, tema
  `DarkAmber`).
- Download via `pytube`, com limpeza do arquivo anterior (`1.mp4`).
- Conversão/processamento com FFmpeg (dependência externa).
- Script antigo de experimentos mantido em `download_teste_antigo.py`.

## Como rodar

> Originalmente escrito para **Windows** (usa PowerShell para instalar
> dependências). Em Linux/macOS, instale as dependências manualmente.

```bash
pip install -r requirements.txt

# instale o FFmpeg e garanta que ele esteja no PATH
# (no original o script esperava o binário em c:\FFMPEG\bin)

python download_video_youtube.py
```

**Observação:** o `pytube` sofre quebras frequentes quando o YouTube muda;
se o download falhar, atualize o pacote (`pip install -U pytube`) ou migre
para `yt-dlp`.

## Licença

MIT — veja [LICENSE](LICENSE).
