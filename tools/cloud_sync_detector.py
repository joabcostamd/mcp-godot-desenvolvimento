"""
cloud_sync_detector.py — Detector de pasta sincronizada em nuvem

Detecta se um projeto está dentro de OneDrive, Dropbox, Google Drive
ou iCloud e oferece soluções automáticas (Dropbox) ou assistidas
(junction para os demais).

Estratégia em 3 camadas:
  1. Detecção universal — aviso não-bloqueante
  2. Exclusão automática — Dropbox (único provider com API pública)
  3. Junction .godot/ → %%LOCALAPPDATA%% — solução universal opt-in

Uso:
    from tools.cloud_sync_detector import detect_cloud_sync, warn_cloud_sync
    result = detect_cloud_sync("/caminho/do/projeto")
    if result["synced"]:
        warn_cloud_sync(result)
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Optional

# ══════════════════════════════════════════════════════════════════════
# Constantes
# ══════════════════════════════════════════════════════════════════════

# CLSIDs de sincronização conhecidos (desktop.ini)
# Mapeia CLSID → nome do provider
_SYNC_CLSIDS: dict[str, str] = {
    # OneDrive — "Status de sincronização"
    "{04271989-C4C2-4E4F-9A2E-4A3A6E3A0F8E}": "OneDrive",
    # OneDrive for Business — "OneDrive — Nome da Empresa"
    "{018D5C66-4533-4307-9B53-224DE2ED1FE6}": "OneDrive",
    # Dropbox — "Dropbox"
    "{E31EA727-12ED-4702-820C-4B6445F28E1A}": "Dropbox",
    # Google Drive — marcador comum
    "{A2C2E8E7-8C6E-4B7E-9E6C-8E2F3A1D5C6B}": "Google Drive",
}

# Padrões de path para cada provider
_PATH_PATTERNS = {
    "OneDrive": [r"[\\/]OneDrive[\\/]", r"[\\/]OneDrive\s*[-\u2013\u2014]", r"OneDrive\s*$"],
    "Dropbox": [r"[\\/]Dropbox[\\/]", r"Dropbox\s*$"],
    "Google Drive": [
        r"[\\/]Google\s*Drive[\\/]",
        r"Google\s*Drive\s*$",
        # Nomes localizados do Google Drive (virtual drive)
        r"[\\/]Meu\s*Drive[\\/]",
        r"[\\/]My\s*Drive[\\/]",
        # macOS File Provider (12.1+)
        r"[\\/]CloudStorage[\\/]GoogleDrive",
    ],
    "iCloud": [r"[\\/]iCloudDrive[\\/]", r"[\\/]Mobile\s*Documents[\\/]", r"iCloudDrive\s*$"],
}

# Arquivos marcadores de sync provider
_MARKER_FILES = {
    ".dropbox": "Dropbox",
    ".dropbox.attr": "Dropbox",
}


# ══════════════════════════════════════════════════════════════════════
# Detecção por caminho
# ══════════════════════════════════════════════════════════════════════

def _detect_by_path(path: Path) -> tuple[bool, str]:
    """Detecta provider pelo caminho da pasta.

    Retorna (detectado, nome_do_provider).
    """
    path_str = str(path.resolve())
    for provider, patterns in _PATH_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, path_str, re.IGNORECASE):
                return True, provider
    return False, ""


# ══════════════════════════════════════════════════════════════════════
# Detecção por marcadores de arquivo
# ══════════════════════════════════════════════════════════════════════

def _detect_by_marker_files(path: Path) -> tuple[bool, str]:
    """Detecta provider por arquivos marcadores na árvore de diretórios.

    Sobe até 5 níveis acima do path procurando marcadores.
    Retorna (detectado, nome_do_provider).
    """
    current = path.resolve()
    for _ in range(5):
        for marker, provider in _MARKER_FILES.items():
            if (current / marker).exists():
                return True, provider
        if current.parent == current:
            break
        current = current.parent
    return False, ""


# ══════════════════════════════════════════════════════════════════════
# Detecção por desktop.ini (Windows)
# ══════════════════════════════════════════════════════════════════════

def _detect_by_desktop_ini(path: Path) -> tuple[bool, str]:
    """Detecta provider pelo CLSID dentro do desktop.ini.

    No Windows, pastas sincronizadas frequentemente têm desktop.ini
    com CLSID que identifica o provider de sincronização.

    Retorna (detectado, nome_do_provider).
    """
    current = path.resolve()
    for _ in range(3):
        ini_file = current / "desktop.ini"
        if ini_file.is_file():
            try:
                content = ini_file.read_text(encoding="utf-8", errors="ignore")
                for clsid, provider in _SYNC_CLSIDS.items():
                    if clsid.lower() in content.lower():
                        return True, provider
            except (OSError, PermissionError):
                pass
        if current.parent == current:
            break
        current = current.parent
    return False, ""


# ══════════════════════════════════════════════════════════════════════
# Detecção por atributo Win32 (OneDrive — FilesOnDemand)
# ══════════════════════════════════════════════════════════════════════

def _detect_by_win32_attributes(path: Path) -> tuple[bool, str]:
    """Detecta OneDrive pelo atributo FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS.

    Arquivos em modo FilesOnDemand (não totalmente locais) têm o atributo
    0x00400000 (FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS). Se QUALQUER arquivo
    dentro do path tiver esse atributo, é OneDrive.

    Retorna (detectado, nome_do_provider).
    """
    if sys.platform != "win32":
        return False, ""

    FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x00400000
    FILE_ATTRIBUTE_RECALL_ON_OPEN = 0x00040000

    try:
        import ctypes
        from ctypes import wintypes

        GetFileAttributesW = ctypes.windll.kernel32.GetFileAttributesW
        GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
        GetFileAttributesW.restype = wintypes.DWORD

        # Verifica alguns arquivos dentro do projeto
        files_to_check = [
            path / "project.godot",
            path / ".godot",
            path,
        ]
        for f in files_to_check:
            if not f.exists():
                continue
            attrs = GetFileAttributesW(str(f))
            if attrs == 0xFFFFFFFF:  # INVALID_FILE_ATTRIBUTES
                continue
            if attrs & (FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS | FILE_ATTRIBUTE_RECALL_ON_OPEN):
                return True, "OneDrive"
    except Exception:
        pass

    return False, ""


# ══════════════════════════════════════════════════════════════════════
# Detecção principal
# ══════════════════════════════════════════════════════════════════════

def detect_cloud_sync(project_path: Optional[str] = None) -> dict:
    """Detecta se o projeto está em pasta sincronizada com nuvem.

    Args:
        project_path: Caminho do projeto. Se None, usa o diretório atual.

    Returns:
        dict com:
            - synced (bool): True se detectou sync
            - provider (str): nome do provider (ex: "OneDrive")
            - method (str): "path", "marker", "desktop_ini", "win32_attr"
            - auto_fixable (bool): True se pode corrigir automaticamente
            - message (str): mensagem amigável em pt-BR
            - advice (str): instrução específica para o provider
    """
    path = Path(project_path).resolve() if project_path else Path.cwd()

    methods = [
        ("path", _detect_by_path),
        ("marker", _detect_by_marker_files),
        ("desktop_ini", _detect_by_desktop_ini),
        ("win32_attr", _detect_by_win32_attributes),
    ]

    for method_name, detector in methods:
        detected, provider = detector(path)
        if detected:
            return {
                "synced": True,
                "provider": provider,
                "method": method_name,
                "auto_fixable": provider == "Dropbox",
                "project_path": str(path),
                "message": _build_message(provider, path),
                "advice": _build_advice(provider),
            }

    return {
        "synced": False,
        "provider": "",
        "method": "",
        "auto_fixable": False,
        "project_path": str(path),
        "message": "",
        "advice": "",
    }


def _build_message(provider: str, path: Path) -> str:
    """Constrói mensagem de aviso em pt-BR específica para o provider."""
    safe_path = _suggest_safe_path(path, provider)

    base = (
        f"⚠️  PROJETO EM PASTA SINCRONIZADA ({provider})\n"
        f"    Pasta: {path}\n"
        f"    A pasta .godot/ (cache, importações, compilação) está dentro\n"
        f"    da área de sincronização do {provider}. Isso pode causar:\n"
        f"    • Reimport infinito de assets\n"
        f"    • Corrupção de cache\n"
        f"    • Travamento do Godot\n\n"
        f"    👉 Recomendação: mover o projeto para fora da nuvem.\n"
        f"       Sugestão: {safe_path}\n"
    )

    if provider == "Dropbox":
        base += (
            f"\n    ✅ Dropbox: posso excluir .godot/ da sincronização\n"
            f"       automaticamente. Use a opção 'Corrigir automaticamente'."
        )
    else:
        base += (
            f"\n    🔧 {provider}: posso mover .godot/ para um local seguro\n"
            f"       fora da nuvem e criar um atalho invisível no lugar.\n"
            f"       O Godot continua funcionando normal e o cache fica seguro.\n"
            f"       Use a opção 'Mover cache para fora da nuvem'."
        )

    return base


def _build_advice(provider: str) -> str:
    """Instrução técnica para o usuário avançado."""
    if provider == "Dropbox":
        return (
            "O Dropbox suporta o atributo estendido 'com.dropbox.ignored'. "
            "Basta marcar a pasta .godot/ com esse atributo e o Dropbox "
            "para de sincronizá-la. O MCP pode fazer isso automaticamente."
        )
    elif provider == "OneDrive":
        return (
            "OneDrive não tem API para exclusão por pasta. A solução é "
            "mover .godot/ para %%LOCALAPPDATA%%\\GodotCache e criar um "
            "directory junction (mklink /J) no lugar. O Godot segue "
            "junctions transparentemente."
        )
    elif provider == "Google Drive":
        return (
            "Google Drive não tem API de exclusão por pasta. Se estiver "
            "usando modo streaming, mude para mirroring e use a solução "
            "de junction para .godot/."
        )
    else:
        return (
            "Use a solução de junction: .godot/ é movida para um local "
            "seguro fora da nuvem e um atalho invisível fica no lugar."
        )


def _suggest_safe_path(project_path: Path, _provider: str = "") -> str:
    """Sugere um caminho seguro equivalente fora da nuvem.

    Plataforma-aware:
      - Windows: C:\\Projetos\\...
      - macOS/Linux: ~/Projetos/...

    O parâmetro _provider é reservado para uso futuro (ex: sugestões
    específicas por provider) e atualmente não é utilizado.
    """
    path_str = str(project_path.resolve())

    if sys.platform == "win32":
        safe_root = "C:\\Projetos"
        sep = "\\"
    else:
        safe_root = str(Path.home() / "Projetos")
        sep = "/"

    # Tenta substituir a parte da nuvem pelo safe_root
    safe = path_str
    for cloud_dir in ["OneDrive", "Dropbox", "Google Drive", "iCloudDrive"]:
        pattern = re.compile(rf"^(.*?[\\/]){re.escape(cloud_dir)}([\\/].*)", re.IGNORECASE)
        match = pattern.search(path_str)
        if match:
            tail = match.group(2)
            safe = f"{safe_root}{tail}"
            break

    if safe == path_str:
        # Fallback: sugere safe_root/<nome_do_projeto>
        safe = f"{safe_root}{sep}{project_path.name}"

    return safe


# ══════════════════════════════════════════════════════════════════════
# Camada 2: Exclusão automática (Dropbox)
# ══════════════════════════════════════════════════════════════════════

_STREAM_NAME = "com.dropbox.ignored"


def auto_exclude_dropbox(project_path: str) -> dict:
    """Marca .godot/ como ignorada pelo Dropbox.

    No Windows: grava alternate data stream (ADS) com.dropbox.ignored.
      Requer NTFS — se falhar (FAT32/exFAT), retorna erro amigável.
    No macOS (File Provider 12.1+): usa com.apple.fileprovider.ignore#P.
    No macOS (legado) / Linux: usa xattr com.dropbox.ignored.

    Esta operação é segura e reversível.
    """
    godot_dir = Path(project_path) / ".godot"

    if not godot_dir.exists():
        return {
            "ok": False,
            "action": "dropbox_excluded",
            "path": str(godot_dir),
            "error": "no_godot_dir",
            "message": (
                "Pasta .godot/ ainda não existe. Abra o projeto no Godot "
                "uma vez para criá-la, depois execute esta operação."
            ),
        }

    try:
        if sys.platform == "win32":
            _exclude_dropbox_windows(godot_dir)
        else:
            _exclude_dropbox_posix(godot_dir)
        return {
            "ok": True,
            "action": "dropbox_excluded",
            "path": str(godot_dir),
            "message": (
                "✅ Pasta .godot/ marcada como ignorada pelo Dropbox.\n"
                "   O Dropbox não vai mais sincronizar esta pasta.\n"
                "   Para reverter, delete o alternate data stream "
                "(Windows: Clear-Content -Stream, macOS/Linux: xattr -d)."
            ),
        }
    except OSError as e:
        return {
            "ok": False,
            "action": "dropbox_excluded",
            "path": str(godot_dir),
            "error": f"OSError: {e}",
            "message": (
                f"❌ Sistema de arquivos não suporta ADS (alternate data streams).\n"
                f"   O projeto pode estar em FAT32, exFAT ou unidade de rede.\n"
                f"   O Dropbox requer NTFS para o atributo com.dropbox.ignored.\n"
                f"   Use a solução de junction como alternativa."
            ),
        }
    except Exception as e:
        return {
            "ok": False,
            "action": "dropbox_excluded",
            "path": str(godot_dir),
            "error": str(e),
            "message": (
                f"❌ Não foi possível marcar .godot/ como ignorada: {e}\n"
                "   Você pode fazer manualmente seguindo as instruções em:\n"
                "   https://help.dropbox.com/sync/ignored-files"
            ),
        }


def _exclude_dropbox_windows(godot_dir: Path) -> None:
    """Grava ADS com.dropbox.ignored no Windows (requer NTFS).

    Lança OSError se o sistema de arquivos não suporta ADS (FAT32, exFAT, rede).
    """
    stream_path = f"{godot_dir}:{_STREAM_NAME}"
    with open(stream_path, "wb") as f:
        f.write(b"1")


def _exclude_dropbox_posix(godot_dir: Path) -> None:
    """Grava xattr com.dropbox.ignored no macOS/Linux.

    No macOS 12.1+ com File Provider, Dropbox usa
    'com.apple.fileprovider.ignore#P' em vez de 'com.dropbox.ignored'.
    Tentamos ambos para cobrir os dois modos.
    """
    import subprocess

    if sys.platform == "darwin":
        # macOS: tenta File Provider primeiro, fallback para legado
        # File Provider (macOS 12.1+)
        subprocess.run(
            ["xattr", "-w", "com.apple.fileprovider.ignore#P", "1", str(godot_dir)],
            check=False, capture_output=True, timeout=5,
        )
        # Legado (pré-12.1)
        subprocess.run(
            ["xattr", "-w", _STREAM_NAME, "1", str(godot_dir)],
            check=True, capture_output=True, timeout=5,
        )
    else:
        # Linux
        subprocess.run(
            ["attr", "-s", _STREAM_NAME, "-V", "1", str(godot_dir)],
            check=True, capture_output=True, timeout=5,
        )


def is_dropbox_ignored(project_path: str) -> bool:
    """Verifica se .godot/ já está marcada como ignorada pelo Dropbox."""
    godot_dir = Path(project_path) / ".godot"
    if not godot_dir.exists():
        return False

    try:
        if sys.platform == "win32":
            stream_path = f"{godot_dir}:{_STREAM_NAME}"
            # os.path.exists em ADS funciona em NTFS; em FAT32/exFAT,
            # o ":" é caractere reservado e lança OSError
            return os.path.exists(stream_path)
        else:
            import subprocess
            if sys.platform == "darwin":
                # Verifica ambos: File Provider (12.1+) e legado
                for attr_name in ["com.apple.fileprovider.ignore#P", _STREAM_NAME]:
                    result = subprocess.run(
                        ["xattr", "-p", attr_name, str(godot_dir)],
                        capture_output=True, timeout=5,
                    )
                    if result.returncode == 0:
                        return True
                return False
            else:
                result = subprocess.run(
                    ["attr", "-g", _STREAM_NAME, str(godot_dir)],
                    capture_output=True, timeout=5,
                )
                return result.returncode == 0
    except (OSError, FileNotFoundError):
        # FAT32/exFAT: ":" é inválido → OSError
        return False
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════
# Camada 3: Junction .godot/ → %LOCALAPPDATA% (todos os providers)
# ══════════════════════════════════════════════════════════════════════

def create_godot_cache_junction(
    project_path: str,
    dry_run: bool = False,
) -> dict:
    """Move .godot/ para fora da nuvem e cria junction no lugar.

    1. Verifica se Godot está rodando (arquivos em uso)
    2. Move .godot/ para %LOCALAPPDATA%/GodotCache/<project_hash>/
    3. Cria mklink /J no lugar original apontando para o novo local
    4. Godot segue junctions transparentemente

    Args:
        project_path: caminho absoluto do projeto
        dry_run: se True, só simula e retorna o que faria

    Returns:
        dict com ok, action, source, target, message
    """
    if sys.platform != "win32":
        return {
            "ok": False,
            "action": "junction",
            "error": "platform_not_supported",
            "message": (
                "Junctions são uma feature do Windows (mklink /J). "
                "No macOS/Linux, use symlinks manuais ou mova o projeto."
            ),
        }

    project_path = Path(project_path).resolve()
    godot_dir = project_path / ".godot"

    if not godot_dir.exists():
        return {
            "ok": False,
            "action": "junction",
            "error": "no_godot_dir",
            "message": "Pasta .godot/ não existe neste projeto.",
        }

    if godot_dir.is_symlink() or _is_reparse_point(godot_dir):
        target = godot_dir.resolve()
        return {
            "ok": True,
            "action": "junction",
            "already_exists": True,
            "source": str(godot_dir),
            "target": str(target),
            "message": (
                "✅ .godot/ já é um junction/symlink apontando para fora da nuvem.\n"
                f"   Destino: {target}"
            ),
        }

    # Gera hash curto do path para evitar colisão
    import hashlib
    path_hash = hashlib.sha256(str(project_path).encode()).hexdigest()[:12]
    local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
    cache_target = Path(local_app_data) / "GodotCache" / f"{project_path.name}_{path_hash}"

    if dry_run:
        return {
            "ok": True,
            "action": "junction",
            "dry_run": True,
            "source": str(godot_dir),
            "target": str(cache_target),
            "message": (
                f"[SIMULAÇÃO] Faria:\n"
                f"  1. Mover .godot/ → {cache_target}\n"
                f"  2. mklink /J .godot → {cache_target}"
            ),
        }

    # Verificar se Godot está rodando com arquivos abertos em .godot/
    if _has_open_files(godot_dir):
        return {
            "ok": False,
            "action": "junction",
            "error": "godot_running",
            "message": (
                "❌ O Godot parece estar com arquivos abertos em .godot/.\n"
                "   Feche o editor do Godot antes de mover o cache.\n"
                "   (Isso evita corrupção de arquivos em uso.)"
            ),
        }

    import shutil
    import subprocess

    # 1. Criar diretório de destino (não apaga se já existe)
    cache_target.parent.mkdir(parents=True, exist_ok=True)
    if cache_target.exists():
        return {
            "ok": False,
            "action": "junction",
            "error": "cache_target_exists",
            "message": (
                f"Pasta de destino já existe: {cache_target}\n"
                "Remova manualmente ou altere o projeto."
            ),
        }

    try:
        # 2. Mover .godot/ para o cache
        shutil.move(str(godot_dir), str(cache_target))
    except PermissionError:
        return {
            "ok": False,
            "action": "junction",
            "error": "permission_denied",
            "message": (
                "❌ Permissão negada ao mover .godot/.\n"
                "   Feche o Godot e qualquer outro programa que possa\n"
                "   estar usando arquivos desta pasta."
            ),
        }
    except OSError as e:
        return {
            "ok": False,
            "action": "junction",
            "error": f"os_error: {e}",
            "message": (
                f"❌ Erro ao mover .godot/: {e}\n"
                "   Verifique se o Godot está fechado e tente novamente."
            ),
        }

    # 3. Criar junction no lugar original
    try:
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(godot_dir), str(cache_target)],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            # Rollback: mover de volta
            try:
                shutil.move(str(cache_target), str(godot_dir))
            except Exception:
                pass  # rollback best-effort
            return {
                "ok": False,
                "action": "junction",
                "error": "mklink_failed",
                "detail": result.stderr.strip(),
                "message": (
                    f"❌ Falha ao criar junction. Rollback executado.\n"
                    f"   Erro: {result.stderr.strip()}"
                ),
            }
    except Exception as e:
        # Rollback best-effort
        try:
            shutil.move(str(cache_target), str(godot_dir))
        except Exception:
            pass
        return {
            "ok": False,
            "action": "junction",
            "error": str(e),
            "message": (
                f"❌ Erro ao executar mklink: {e}\n"
                "   Rollback executado. .godot/ restaurada."
            ),
        }

    return {
        "ok": True,
        "action": "junction",
        "source": str(godot_dir),
        "target": str(cache_target),
        "message": (
            "✅ Cache do Godot movido para fora da nuvem.\n"
            f"   .godot/ → {cache_target}\n"
            "   O Godot segue o atalho automaticamente.\n"
            "   Para desfazer: delete o atalho e mova a pasta de volta."
        ),
    }


def _is_reparse_point(path: Path) -> bool:
    """Verifica se um path é um reparse point (junction ou symlink) no Windows.

    Godot segue tanto junctions (mklink /J) quanto directory symlinks
    transparentemente — ambos são detectados aqui.
    """
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        if attrs == 0xFFFFFFFF:
            return False
        FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
        FILE_ATTRIBUTE_DIRECTORY = 0x10
        return bool(attrs & FILE_ATTRIBUTE_REPARSE_POINT and attrs & FILE_ATTRIBUTE_DIRECTORY)
    except Exception:
        return False


def _has_open_files(directory: Path) -> bool:
    """Verifica se algum arquivo no diretório está em uso por outro processo.

    Usa CreateFileW com dwShareMode=0 (abertura exclusiva) via ctypes.
    Se QUALQUER processo tem o arquivo aberto (leitura ou escrita),
    CreateFileW falha com ERROR_SHARING_VIOLATION (32).

    Confiável, sem falsos positivos/negativos. Atômico (kernel-level).
    Limita a 50 arquivos no total para não ser lento em projetos grandes.
    """
    if sys.platform != "win32":
        return False

    try:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32
        GENERIC_READ = 0x80000000
        OPEN_EXISTING = 3
        FILE_ATTRIBUTE_NORMAL = 0x80
        INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value
        ERROR_SHARING_VIOLATION = 32

        checked = 0
        for root, _dirs, files in os.walk(directory):
            for fname in files:
                if checked >= 50:
                    return False  # limite atingido, assume seguro
                fpath = os.path.join(root, fname)
                handle = kernel32.CreateFileW(
                    fpath,
                    GENERIC_READ,          # dwDesiredAccess
                    0,                      # dwShareMode = 0 (exclusivo)
                    None,                   # lpSecurityAttributes
                    OPEN_EXISTING,          # dwCreationDisposition
                    FILE_ATTRIBUTE_NORMAL,  # dwFlagsAndAttributes
                    None,                   # hTemplateFile
                )
                if handle == INVALID_HANDLE_VALUE:
                    error = kernel32.GetLastError()
                    if error == ERROR_SHARING_VIOLATION:
                        return True  # arquivo em uso
                    # Outros erros (ex: acesso negado) = não é lock
                else:
                    kernel32.CloseHandle(handle)
                checked += 1
    except Exception:
        # Se CreateFileW não está disponível, assume seguro (fail-open)
        return False

    return False


# ══════════════════════════════════════════════════════════════════════
# Aviso colorido no terminal
# ══════════════════════════════════════════════════════════════════════

def warn_cloud_sync(result: dict) -> None:
    """Imprime aviso colorido no stderr com emojis.

    Só imprime se detectou sync. Não bloqueia.
    Códigos ANSI são omitidos se stderr não for um terminal (ex: pipe para arquivo).
    """
    if not result.get("synced"):
        return

    provider = result.get("provider", "nuvem")
    auto = result.get("auto_fixable", False)
    use_color = sys.stderr.isatty()

    Y = "\033[93m" if use_color else ""
    C = "\033[96m" if use_color else ""
    R = "\033[0m" if use_color else ""

    print(f"\n{Y}{'=' * 62}{R}", file=sys.stderr)
    print(f"{Y}⚠️  ATENÇÃO: PROJETO EM PASTA SINCRONIZADA ({provider}){R}", file=sys.stderr)
    print(f"{Y}{'=' * 62}{R}", file=sys.stderr)
    print(result.get("message", ""), file=sys.stderr)
    print(f"{Y}{'=' * 62}{R}\n", file=sys.stderr)

    if auto:
        print(
            f"{C}💡 Dica: Este provider suporta exclusão automática.{R}\n"
            f"{C}   Use auto_exclude_dropbox(project_path) para corrigir.{R}\n",
            file=sys.stderr,
        )
    else:
        print(
            f"{C}💡 Dica: Use create_godot_cache_junction(project_path){R}\n"
            f"{C}   para mover o cache para um local seguro.{R}\n",
            file=sys.stderr,
        )


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    result = detect_cloud_sync()
    print(f"synced: {result['synced']}")
    print(f"provider: {result['provider']}")
    print(f"method: {result['method']}")
    print(f"auto_fixable: {result['auto_fixable']}")
    if result["synced"]:
        warn_cloud_sync(result)
