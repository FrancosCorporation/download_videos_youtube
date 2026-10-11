#!/usr/bin/env python3

"""Interface desktop para baixar um vídeo do YouTube em MP4."""

from __future__ import annotations

import queue
import re
import socket
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

import FreeSimpleGUI as sg
from pytubefix import YouTube

NETWORK_TIMEOUT_SECONDS = 30
MAX_DOWNLOAD_RETRIES = 3
ALLOWED_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}


class DownloadCancelled(Exception):
    """Indica que o usuário interrompeu o download."""


def normalize_video_url(raw_url: str) -> str:
    """Valida uma URL de vídeo e devolve sua forma canônica HTTPS."""
    value = (raw_url or "").strip()
    if not value:
        raise ValueError("Informe a URL de um vídeo do YouTube.")
    if "://" not in value:
        value = f"https://{value}"

    try:
        parsed = urlsplit(value)
        host = (parsed.hostname or "").lower().rstrip(".")
        port = parsed.port
    except ValueError as error:
        raise ValueError("A URL informada não é válida.") from error

    if parsed.scheme.lower() not in {"http", "https"}:
        raise ValueError("A URL deve usar HTTP ou HTTPS.")
    if host not in ALLOWED_YOUTUBE_HOSTS or parsed.username or parsed.password:
        raise ValueError("Informe uma URL de vídeo do YouTube.")
    if port is not None:
        raise ValueError("A URL não pode usar uma porta personalizada.")

    if host == "youtu.be":
        video_id = parsed.path.strip("/")
        if "/" in video_id:
            video_id = ""
    elif parsed.path.rstrip("/") == "/watch":
        video_ids = parse_qs(parsed.query).get("v", [])
        video_id = video_ids[0] if len(video_ids) == 1 else ""
    else:
        video_id = ""

    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError("A URL não contém um ID válido de vídeo do YouTube.")

    return urlunsplit(
        ("https", "www.youtube.com", "/watch", urlencode({"v": video_id}), "")
    )


def get_default_output_directory() -> Path:
    downloads = Path.home() / "Downloads"
    return downloads if downloads.is_dir() else Path.home()


def format_bytes(byte_count: int) -> str:
    value = float(byte_count)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


def build_output_path(destination: Path, title: str, video_id: str) -> Path:
    safe_title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", title)
    safe_title = safe_title.strip(" .")[:100].rstrip(" .") or "video"
    stem = f"{safe_title} [{video_id}]"
    candidate = destination / f"{stem}.mp4"
    suffix = 1
    while candidate.exists():
        candidate = destination / f"{stem} ({suffix}).mp4"
        suffix += 1
    return candidate


def download_video(
    video_url: str,
    destination: Path,
    progress_events: queue.Queue,
    cancel_event: threading.Event,
) -> Path:
    socket.setdefaulttimeout(NETWORK_TIMEOUT_SECONDS)
    youtube = YouTube(video_url)
    if cancel_event.is_set():
        raise DownloadCancelled

    stream = youtube.streams.get_highest_resolution()
    if stream is None:
        raise RuntimeError("Não há uma versão MP4 disponível para este vídeo.")

    destination.mkdir(parents=True, exist_ok=True)
    output_path = build_output_path(destination, youtube.title, youtube.video_id)
    temporary_path = output_path.with_name(f".{output_path.name}.part")
    last_progress_update = 0.0

    def report_progress(_stream, _chunk, bytes_remaining):
        nonlocal last_progress_update
        total_bytes = stream.filesize or stream.filesize_approx or 0
        now = time.monotonic()
        if total_bytes <= 0 or now - last_progress_update < 0.15:
            return
        last_progress_update = now
        progress_events.put(("progress", total_bytes - bytes_remaining, total_bytes))

    youtube.register_on_progress_callback(report_progress)

    try:
        downloaded_path = stream.download(
            output_path=str(destination),
            filename=temporary_path.name,
            skip_existing=False,
            timeout=NETWORK_TIMEOUT_SECONDS,
            max_retries=MAX_DOWNLOAD_RETRIES,
            interrupt_checker=cancel_event.is_set,
        )
        if cancel_event.is_set() or downloaded_path is None:
            raise DownloadCancelled
        Path(downloaded_path).replace(output_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    return output_path


def download_worker(video_url, destination, progress_events, cancel_event):
    try:
        output_path = download_video(
            video_url, destination, progress_events, cancel_event
        )
    except DownloadCancelled:
        progress_events.put(("cancelled",))
    except Exception as error:
        message = str(error).strip() or error.__class__.__name__
        progress_events.put(("error", message))
    else:
        progress_events.put(("complete", str(output_path)))


def set_busy_state(window, busy: bool) -> None:
    window["-URL-"].update(disabled=busy)
    window["-DESTINATION-"].update(disabled=busy)
    window["-BROWSE-"].update(disabled=busy)
    window["-DOWNLOAD-"].update(disabled=busy)
    window["-CANCEL-"].update(disabled=not busy)


def build_window():
    layout = [
        [sg.Text("URL do vídeo")],
        [
            sg.Input(key="-URL-", expand_x=True),
        ],
        [sg.Text("Salvar em")],
        [
            sg.Input(
                default_text=str(get_default_output_directory()),
                key="-DESTINATION-",
                expand_x=True,
            ),
            sg.FolderBrowse("Escolher pasta", target="-DESTINATION-", key="-BROWSE-"),
        ],
        [sg.ProgressBar(100, orientation="h", size=(40, 12), key="-PROGRESS-")],
        [
            sg.Text(
                "Pronto para baixar. O arquivo será salvo em MP4.",
                key="-STATUS-",
                size=(80, 2),
                expand_x=True,
            )
        ],
        [
            sg.Button("Baixar vídeo", key="-DOWNLOAD-", bind_return_key=True),
            sg.Button("Cancelar download", key="-CANCEL-", disabled=True),
            sg.Button("Sair", key="-EXIT-"),
        ],
    ]
    return sg.Window(
        "Baixar vídeo do YouTube",
        layout,
        size=(720, 270),
        resizable=True,
        finalize=True,
        enable_close_attempted_event=True,
    )


def main() -> int:
    sg.theme("DarkAmber")
    window = build_window()
    progress_events = None
    cancel_event = None
    worker_thread = None
    close_when_finished = False

    try:
        while True:
            event, values = window.read(timeout=100)

            if event in (sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT, "-EXIT-"):
                if worker_thread and worker_thread.is_alive():
                    close_when_finished = True
                    cancel_event.set()
                    window["-STATUS-"].update(
                        "Interrompendo o download antes de sair..."
                    )
                    window["-EXIT-"].update(disabled=True)
                    continue
                break

            if event == "-CANCEL-" and cancel_event is not None:
                cancel_event.set()
                window["-STATUS-"].update("Interrompendo o download...")
                window["-CANCEL-"].update(disabled=True)

            if event == "-DOWNLOAD-" and (
                not worker_thread or not worker_thread.is_alive()
            ):
                try:
                    video_url = normalize_video_url(values["-URL-"] or "")
                    destination = Path(values["-DESTINATION-"]).expanduser().resolve()
                    destination.mkdir(parents=True, exist_ok=True)
                except (OSError, ValueError) as error:
                    sg.popup_error(str(error), title="Não foi possível iniciar")
                    continue

                progress_events = queue.Queue()
                cancel_event = threading.Event()
                worker_thread = threading.Thread(
                    target=download_worker,
                    args=(video_url, destination, progress_events, cancel_event),
                    daemon=True,
                )
                window["-PROGRESS-"].update(current_count=0)
                window["-STATUS-"].update("Conectando ao YouTube...")
                set_busy_state(window, True)
                worker_thread.start()

            if progress_events is not None:
                while True:
                    try:
                        message = progress_events.get_nowait()
                    except queue.Empty:
                        break

                    if message[0] == "progress":
                        _, downloaded, total = message
                        percentage = min(int(downloaded * 100 / total), 100)
                        window["-PROGRESS-"].update(current_count=percentage)
                        window["-STATUS-"].update(
                            f"Baixando: {percentage}% "
                            f"({format_bytes(downloaded)} de {format_bytes(total)})"
                        )
                    elif message[0] == "complete":
                        window["-PROGRESS-"].update(current_count=100)
                        window["-STATUS-"].update(f"Download concluído: {message[1]}")
                        set_busy_state(window, False)
                    elif message[0] == "cancelled":
                        window["-PROGRESS-"].update(current_count=0)
                        window["-STATUS-"].update("Download cancelado.")
                        set_busy_state(window, False)
                    elif message[0] == "error":
                        window["-PROGRESS-"].update(current_count=0)
                        window["-STATUS-"].update("O download não foi concluído.")
                        set_busy_state(window, False)
                        sg.popup_error(message[1], title="Falha no download")

            if worker_thread and not worker_thread.is_alive():
                worker_thread = None
                progress_events = None
                cancel_event = None
                if close_when_finished:
                    break
    finally:
        window.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
