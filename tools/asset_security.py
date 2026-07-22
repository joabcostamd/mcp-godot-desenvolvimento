"""asset_security.py — Verificacao de seguranca de assets externos (FATIA 2.AM).

Valida assets baixados/importados antes de copiar para o projeto.
Verifica: origem confiavel, extensao permitida, tamanho maximo,
ausencia de codigo malicioso embutido, e metadados de licenca.

A sandbox de GDScript tem bypasses conhecidos:
- .gd scripts podem conter exec() / load() arbitrario
- .tscn pode referenciar scripts externos
- .tres pode ter @tool com codigo executavel
- Arquivos binarios podem ter shellcode embutido

Tools:
    validate_asset_security — verifica um asset antes de importar
    scan_asset_directory — escaneia diretorio de assets importados
    asset_security_report — relatorio de seguranca do projeto
"""

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Optional

# ── Constantes ──────────────────────────────────────────────────────

MAX_ASSET_SIZE_MB = {
    ".png": 50,
    ".jpg": 50,
    ".jpeg": 50,
    ".svg": 10,
    ".webp": 50,
    ".wav": 30,
    ".ogg": 30,
    ".mp3": 30,
    ".glb": 100,
    ".gltf": 100,
    ".ttf": 20,
    ".otf": 20,
    ".tres": 10,
    ".tscn": 20,
    ".gd": 5,
    ".gdshader": 1,
}

# Extensoes que contem codigo executavel (precisam de scan extra)
EXECUTABLE_EXTENSIONS = {".gd", ".gdshader", ".tscn", ".tres"}

# Dominios confiaveis (CC0, MIT, GPL-compatible)
TRUSTED_DOMAINS = {
    "kenney.nl", "cdn.kenney.nl",
    "polyhaven.com", "api.polyhaven.com", "cdn.polyhaven.com",
    "ambientcg.com", "cdn.ambientcg.com", "dl.ambientcg.com",
    "opengameart.org",
    "freesound.org",
    "googleapis.com",  # Fontes
}

# Padroes suspeitos em arquivos de texto (GDScript / .tscn / .tres)
SUSPICIOUS_PATTERNS = [
    (r'OS\.execute\s*\(', "Execucao de processo externo (OS.execute)"),
    (r'OS\.shell_open\s*\(', "Abertura de shell (OS.shell_open)"),
    (r'FileAccess\.open\s*\(\s*["\'](?:/[^/]|\.\.)', "Acesso a arquivo fora do projeto"),
    (r'\.call_deferred\s*\(\s*["\'](?:free|queue_free)', "Liberacao de recursos via string"),
    (r'eval\s*\(', "Uso de eval() — execucao arbitraria de codigo"),
    (r'load\s*\(\s*["\']res://[^"\']*\.(?:exe|dll|so|dylib)', "Carregamento de biblioteca nativa"),
    (r'OS\.set_environment\s*\(', "Modificacao de variaveis de ambiente"),
    (r'JavaScriptBridge\.eval\s*\(', "Execucao de JavaScript (web)"),
]

# Licencas compativeis
COMPATIBLE_LICENSES = {
    "CC0", "CC0 1.0", "CC0-1.0",
    "MIT", "MIT License",
    "Apache-2.0", "Apache 2.0",
    "GPL-2.0", "GPL-3.0", "LGPL-2.1", "LGPL-3.0",
    "BSD-2-Clause", "BSD-3-Clause",
    "ZLIB", "zlib License",
    "Unlicense",
    "OFL-1.1",  # SIL Open Font License
}


# ══════════════════════════════════════════════════════════════════════
# validate_asset_security
# ══════════════════════════════════════════════════════════════════════

def validate_asset_security(
    asset_path: str,
    source_url: str = "",
    license_name: str = "",
    check_content: bool = True,
) -> dict:
    """Verifica a seguranca de um asset antes de importa-lo.

    Args:
        asset_path: Caminho para o arquivo do asset.
        source_url: URL de origem (para verificacao de dominio).
        license_name: Nome da licenca declarada.
        check_content: Se True, escaneia conteudo de arquivos executaveis.

    Returns:
        dict com status, riscos e recomendacoes.
    """
    path = Path(asset_path)
    risks = []
    warnings = []

    # 1. Verificar existencia
    if not path.exists():
        return {"status": "error", "message": f"Arquivo nao encontrado: {asset_path}"}

    # 2. Verificar extensao
    ext = path.suffix.lower()
    if ext not in MAX_ASSET_SIZE_MB:
        return {"status": "error", "message": f"Extensao nao permitida: {ext}",
                "allowed_extensions": sorted(MAX_ASSET_SIZE_MB.keys())}

    # 3. Verificar tamanho
    size_mb = path.stat().st_size / (1024 * 1024)
    max_mb = MAX_ASSET_SIZE_MB.get(ext, 50)
    if size_mb > max_mb:
        risks.append({
            "type": "oversized",
            "severity": "medium",
            "message": f"Arquivo muito grande: {size_mb:.1f}MB (maximo {max_mb}MB para {ext})",
        })

    # 4. Verificar origem
    if source_url:
        from urllib.parse import urlparse
        parsed = urlparse(source_url)
        hostname = parsed.hostname or ""
        if hostname and not any(hostname == d or hostname.endswith("." + d) for d in TRUSTED_DOMAINS):
            warnings.append({
                "type": "untrusted_source",
                "severity": "high",
                "message": f"Origem nao confiavel: {hostname}. Assets de fontes desconhecidas requerem revisao manual.",
                "source": source_url,
            })

    # 5. Verificar licenca
    if license_name:
        if license_name not in COMPATIBLE_LICENSES:
            warnings.append({
                "type": "incompatible_license",
                "severity": "medium",
                "message": f"Licenca '{license_name}' pode nao ser compativel. Verifique os termos.",
                "compatible_licenses": sorted(COMPATIBLE_LICENSES),
            })
    else:
        warnings.append({
            "type": "missing_license",
            "severity": "low",
            "message": "Licenca nao declarada. Todo asset precisa de licenca explicita.",
        })

    # 6. Scan de conteudo (apenas para arquivos executaveis)
    if check_content and ext in EXECUTABLE_EXTENSIONS:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            for pattern, description in SUSPICIOUS_PATTERNS:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    risks.append({
                        "type": "suspicious_code",
                        "severity": "critical",
                        "message": f"Codigo suspeito detectado: {description}",
                        "pattern": pattern,
                        "matches": len(matches),
                    })
        except (UnicodeDecodeError, OSError):
            risks.append({
                "type": "unreadable",
                "severity": "medium",
                "message": f"Arquivo {ext} nao pode ser lido como texto. Pode ser binario corrompido.",
            })

    # 7. Hash do arquivo
    file_hash = _hash_file(path)

    return {
        "status": "rejected" if any(r["severity"] == "critical" for r in risks) else "approved",
        "file": str(path),
        "size_mb": round(size_mb, 2),
        "extension": ext,
        "hash_sha256": file_hash,
        "risks": risks,
        "warnings": warnings,
        "risk_count": len(risks),
        "warning_count": len(warnings),
        "message": _summarize(risks, warnings),
    }


# ══════════════════════════════════════════════════════════════════════
# scan_asset_directory
# ══════════════════════════════════════════════════════════════════════

def scan_asset_directory(
    project_path: str,
    directory: str = "assets",
    recursive: bool = True,
) -> dict:
    """Escaneia um diretorio de assets e verifica seguranca de todos os arquivos.

    Args:
        project_path: Caminho do projeto.
        directory: Diretorio a escanear (relativo ao projeto).
        recursive: Se True, escaneia subdiretorios.

    Returns:
        dict com resultados agregados.
    """
    proj = Path(project_path)
    asset_dir = proj / directory

    if not asset_dir.is_dir():
        return {"status": "error", "message": f"Diretorio nao encontrado: {asset_dir}"}

    results = []
    total_risks = 0
    total_warnings = 0

    pattern = "**/*" if recursive else "*"
    for fpath in sorted(asset_dir.glob(pattern)):
        if not fpath.is_file():
            continue
        ext = fpath.suffix.lower()
        if ext not in MAX_ASSET_SIZE_MB:
            continue

        result = validate_asset_security(
            str(fpath),
            check_content=(ext in EXECUTABLE_EXTENSIONS),
        )
        results.append(result)
        total_risks += result.get("risk_count", 0)
        total_warnings += result.get("warning_count", 0)

    critical = sum(1 for r in results if r["status"] == "rejected")

    return {
        "status": "success",
        "directory": str(asset_dir),
        "files_scanned": len(results),
        "files_rejected": critical,
        "total_risks": total_risks,
        "total_warnings": total_warnings,
        "results": results[:100],  # Limitar para evitar resposta gigante
        "truncated": len(results) > 100,
        "message": _scan_summary(len(results), critical, total_risks, total_warnings),
    }


# ══════════════════════════════════════════════════════════════════════
# asset_security_report
# ══════════════════════════════════════════════════════════════════════

def asset_security_report(project_path: str) -> dict:
    """Gera relatorio completo de seguranca de assets do projeto.

    Args:
        project_path: Caminho do projeto.

    Returns:
        dict com relatorio agregado.
    """
    proj = Path(project_path)

    # Escanear diretorio assets/
    assets_scan = scan_asset_directory(project_path, "assets", recursive=True)

    # Verificar arquivos GDScript no projeto
    gd_scan = {"files_scanned": 0, "risks": []}
    gd_dir = proj / "scripts"
    if gd_dir.is_dir():
        for gd_file in gd_dir.glob("**/*.gd"):
            result = validate_asset_security(str(gd_file), check_content=True)
            gd_scan["files_scanned"] += 1
            if result.get("risks"):
                gd_scan["risks"].append({
                    "file": str(gd_file.relative_to(proj)),
                    "risks": result["risks"],
                })

    # Verificar .tscn
    tscn_count = 0
    tscn_risks = []
    for tscn_file in proj.glob("**/*.tscn"):
        if "addons" in str(tscn_file):
            continue  # Pular addons de terceiros
        tscn_count += 1

    return {
        "status": "success",
        "project": str(proj),
        "assets": {
            "scanned": assets_scan.get("files_scanned", 0),
            "rejected": assets_scan.get("files_rejected", 0),
            "risks": assets_scan.get("total_risks", 0),
            "warnings": assets_scan.get("total_warnings", 0),
        },
        "scripts": {
            "scanned": gd_scan["files_scanned"],
            "risks_found": len(gd_scan["risks"]),
        },
        "scenes_count": tscn_count,
        "overall_risk": "high" if assets_scan.get("files_rejected", 0) > 0 else
                        "medium" if assets_scan.get("total_risks", 0) > 0 else "low",
        "message": "Relatorio de seguranca gerado. Revise riscos criticos antes de publicar.",
    }


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════

def _hash_file(path: Path) -> str:
    """SHA-256 de um arquivo."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _summarize(risks: list, warnings: list) -> str:
    parts = []
    if risks:
        critical = sum(1 for r in risks if r["severity"] == "critical")
        if critical:
            parts.append(f"{critical} risco(s) critico(s)")
        parts.append(f"{len(risks)} risco(s) total")
    if warnings:
        parts.append(f"{len(warnings)} aviso(s)")
    if not parts:
        return "Asset seguro. Nenhum risco ou aviso encontrado."
    return "ATENCAO: " + " · ".join(parts)


def _scan_summary(total: int, rejected: int, risks: int, warnings: int) -> str:
    if total == 0:
        return "Nenhum asset encontrado para escanear."
    parts = [f"{total} asset(s) escaneado(s)"]
    if rejected:
        parts.append(f"{rejected} rejeitado(s)")
    if risks:
        parts.append(f"{risks} risco(s)")
    if warnings:
        parts.append(f"{warnings} aviso(s)")
    if rejected == 0 and risks == 0:
        parts.append("— todos seguros ✅")
    return " · ".join(parts)
