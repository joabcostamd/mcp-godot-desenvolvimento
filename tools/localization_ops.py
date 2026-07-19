"""localization_ops.py — Testes de Internacionalização (i18n) — Fatia 4.1.

Validação de traduções: strings faltantes, overflow de texto com locale
longo, e contraste texto/fundo (WCAG). Reutiliza capture_ui_snapshot (1.3),
detect_ui_overlaps (1.4) e generate_ui_overlay (1.5).

Ops do rollup localization_manage: find_missing, detect_overflow, check_contrast.
"""

import csv
import io
import re
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════

def _get_proj(project_path: str | None = None) -> Path:
    """Resolve o caminho do projeto ativo."""
    from tools.project_ops import _get_active_project as gap
    return Path(project_path) if project_path else Path(gap())


def _read_translation_csv(proj: Path) -> dict | None:
    """Lê locales/translations.csv e retorna {header, keys: {key: {locale: text}}}.

    Returns None se o CSV não existir.
    """
    csv_path = proj / "locales" / "translations.csv"
    if not csv_path.exists():
        return None
    content = csv_path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(content))
    header = reader.fieldnames or []
    locales = [h for h in header if h != "key"]
    keys = {}
    for row in reader:
        k = row.get("key", "").strip()
        if not k:
            continue
        keys[k] = {loc: row.get(loc, "") for loc in locales}
    return {"header": header, "locales": locales, "keys": keys, "csv_path": str(csv_path)}


def _scan_tscn_for_strings(proj: Path) -> list[str]:
    """Varre todos os .tscn do projeto e extrai strings de texto visível.

    Busca atributos: text, placeholder_text, title, hint_text, window_title
    em nós Control (Label, Button, LineEdit, Window, OptionButton, etc.).
    """
    strings: list[str] = []
    # Padrões para extrair texto de atributos comuns
    text_patterns = [
        re.compile(r'text\s*=\s*"([^"]*)"'),
        re.compile(r"text\s*=\s*'([^']*)'"),
        re.compile(r'placeholder_text\s*=\s*"([^"]*)"'),
        re.compile(r"placeholder_text\s*=\s*'([^']*)'"),
        re.compile(r'title\s*=\s*"([^"]*)"'),
        re.compile(r"title\s*=\s*'([^']*)'"),
        re.compile(r'hint_text\s*=\s*"([^"]*)"'),
        re.compile(r"hint_text\s*=\s*'([^']*)'"),
        re.compile(r'window_title\s*=\s*"([^"]*)"'),
        re.compile(r"window_title\s*=\s*'([^']*)'"),
    ]

    for tscn in proj.rglob("*.tscn"):
        # Pula addons e .godot
        if "addons" in tscn.parts or ".godot" in tscn.parts:
            continue
        try:
            content = tscn.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat in text_patterns:
            for match in pat.finditer(content):
                text = match.group(1).strip()
                if text and len(text) > 1:  # Ignora textos vazios ou single-char
                    strings.append(text)
    return strings


def _scan_gd_for_tr_calls(proj: Path) -> list[str]:
    """Varre todos os .gd do projeto e extrai strings de chamadas tr().

    Busca: tr("..."), tr('...'), TranslationServer.translate("...").
    """
    strings: list[str] = []
    tr_patterns = [
        re.compile(r'tr\s*\(\s*"([^"]*)"'),
        re.compile(r"tr\s*\(\s*'([^']*)'"),
        re.compile(r'TranslationServer\.translate\s*\(\s*"([^"]*)"'),
    ]

    for gd in proj.rglob("*.gd"):
        if "addons" in gd.parts or ".godot" in gd.parts:
            continue
        try:
            content = gd.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat in tr_patterns:
            for match in pat.finditer(content):
                text = match.group(1).strip()
                if text:
                    strings.append(text)
    return strings


def _estimate_text_width(text: str, font_size: int = 14) -> float:
    """Estima largura do texto em pixels com base no charset.

    Heurística:
    - CJK (chinês/japonês/coreano): ~1.0 * font_size por char
    - Cirílico/árabe: ~0.75 * font_size por char
    - Latim: ~0.6 * font_size por char
    - Dígitos/pontuação: ~0.5 * font_size por char
    """
    cjk_ranges = [
        (0x4E00, 0x9FFF), (0x3400, 0x4DBF),  # CJK Unified
        (0xAC00, 0xD7AF),  # Hangul
        (0x3040, 0x309F), (0x30A0, 0x30FF),  # Hiragana/Katakana
    ]
    cyrillic_ranges = [(0x0400, 0x04FF), (0x0500, 0x052F)]
    arabic_ranges = [(0x0600, 0x06FF), (0x0750, 0x077F)]

    def _in_range(cp: int, ranges: list) -> bool:
        return any(lo <= cp <= hi for lo, hi in ranges)

    width = 0.0
    for ch in text:
        cp = ord(ch)
        if _in_range(cp, cjk_ranges):
            width += font_size * 1.0
        elif _in_range(cp, cyrillic_ranges) or _in_range(cp, arabic_ranges):
            width += font_size * 0.75
        elif ch.isdigit() or ch in ",.;:!?\"'()-_ ":
            width += font_size * 0.5
        else:
            width += font_size * 0.6
    return width


def _rgb_to_luminance(r: int, g: int, b: int) -> float:
    """Calcula luminância relativa (WCAG 2.0) de uma cor RGB (0-255)."""
    def _linearize(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Converte cor hex #rrggbb ou #rgb para (r, g, b)."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _wcag_contrast_ratio(rgb1: tuple, rgb2: tuple) -> float:
    """Calcula razão de contraste WCAG entre duas cores RGB."""
    l1 = _rgb_to_luminance(*rgb1)
    l2 = _rgb_to_luminance(*rgb2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ══════════════════════════════════════════════════════════════════════
# Op 1 — find_missing_translations
# ══════════════════════════════════════════════════════════════════════

def find_missing_translations(
    project_path: str | None = None,
) -> dict:
    """Encontra strings do jogo sem tradução no CSV de localização.

    Varre todos os .tscn (texto de Labels, Buttons, etc.) e .gd
    (chamadas tr()) do projeto, cruza com locales/translations.csv,
    e lista strings que não têm tradução em cada locale.

    Args:
        project_path: Caminho do projeto (auto-detecta se None).

    Returns:
        {"status": "success", "csv_path": str, "locales": [...],
         "total_keys": int, "game_strings": int,
         "missing": [{"key": str, "source_file": str,
          "missing_locales": [...]}],
         "total_missing": int}
    """
    proj = _get_proj(project_path)
    csv_data = _read_translation_csv(proj)

    if csv_data is None:
        return {
            "status": "error",
            "message": (
                "CSV de tradução não encontrado em locales/translations.csv. "
                "Execute setup_localization primeiro."
            ),
        }

    locales = csv_data["locales"]
    existing_keys = set(csv_data["keys"].keys())

    # Coleta strings do jogo
    tscn_strings = _scan_tscn_for_strings(proj)
    gd_strings = _scan_gd_for_tr_calls(proj)
    all_game_strings = list(set(tscn_strings + gd_strings))

    # Verifica quais game strings NÃO estão no CSV
    missing = []
    for s in all_game_strings:
        if s not in existing_keys:
            # Tenta descobrir de qual arquivo veio
            source = "unknown"
            for tscn in proj.rglob("*.tscn"):
                if "addons" in tscn.parts or ".godot" in tscn.parts:
                    continue
                try:
                    if s in tscn.read_text(encoding="utf-8", errors="ignore"):
                        source = str(tscn.relative_to(proj))
                        break
                except Exception:
                    continue
            if source == "unknown":
                for gd in proj.rglob("*.gd"):
                    if "addons" in gd.parts or ".godot" in gd.parts:
                        continue
                    try:
                        if s in gd.read_text(encoding="utf-8", errors="ignore"):
                            source = str(gd.relative_to(proj))
                            break
                    except Exception:
                        continue

            missing.append({
                "key": s,
                "source_file": source,
                "missing_locales": list(locales),
            })

    # Verifica quais chaves existentes têm traduções faltando em algum locale
    for key, translations in csv_data["keys"].items():
        missing_locales = [loc for loc in locales if not translations.get(loc, "").strip()]
        if missing_locales:
            # Verifica se já está na lista
            existing = [m for m in missing if m["key"] == key]
            if not existing:
                missing.append({
                    "key": key,
                    "source_file": "locales/translations.csv",
                    "missing_locales": missing_locales,
                })

    return {
        "status": "success",
        "csv_path": csv_data["csv_path"],
        "locales": locales,
        "total_keys": len(existing_keys),
        "game_strings": len(all_game_strings),
        "missing": missing,
        "total_missing": len(missing),
    }


# ══════════════════════════════════════════════════════════════════════
# Op 2 — detect_text_overflow
# ══════════════════════════════════════════════════════════════════════

def detect_text_overflow(
    scene_path: str,
    locale: str = "de",
    project_path: str | None = None,
    font_size: int = 14,
) -> dict:
    """Detecta texto que estoura os limites do container com um locale longo.

    Usa capture_ui_snapshot (1.3) para obter Rect2 de todos os Controls.
    Para cada Control com texto (Label, Button, etc.), estima a largura
    do texto traduzido e compara com a largura do container.

    Args:
        scene_path: Caminho da cena .tscn.
        locale: Locale para teste de overflow (default "de" — alemão).
        project_path: Caminho do projeto (auto-detecta se None).
        font_size: Tamanho da fonte para estimativa (default 14).

    Returns:
        {"status": "success", "overflows": [{...}], "total_overflows": int}
    """
    from tools.runtime_ui import capture_ui_snapshot

    proj = _get_proj(project_path)
    csv_data = _read_translation_csv(proj)

    # Obtém snapshot da UI
    snapshot = capture_ui_snapshot(scene_path, str(proj))
    if snapshot.get("status") != "success":
        return snapshot

    controls = snapshot.get("controls", [])
    visible_controls = [c for c in controls if c.get("visible", True)]

    # Constrói lookup de traduções se CSV existir
    translations_lookup: dict[str, str] = {}
    if csv_data and locale in csv_data.get("locales", []):
        for key, trans in csv_data["keys"].items():
            translations_lookup[key] = trans.get(locale, key)

    overflows = []
    for ctrl in visible_controls:
        ctrl_type = ctrl.get("type", "")
        # Só verifica controles que tipicamente têm texto
        if not any(t in ctrl_type for t in ("Label", "Button", "Edit", "Option", "Menu", "Check", "Window")):
            continue

        rect = ctrl.get("rect2", {})
        container_w = rect.get("w", 0)
        if container_w <= 0:
            continue

        # Tenta obter o texto original do controle
        # No modo file-based, precisamos acessar as props do .tscn
        # Vamos usar uma heurística: o nome do controle às vezes contém texto
        ctrl_name = ctrl.get("name", "")

        # Tenta ler o texto do .tscn diretamente
        original_text = ""
        try:
            full_path = proj / scene_path
            if full_path.exists():
                content = full_path.read_text(encoding="utf-8", errors="ignore")
                # Procura o texto dentro do nó específico usando regex aproximada
                # Busca por: [node name="NOME"...] ... text = "TEXTO"
                name_escaped = re.escape(ctrl_name)
                node_pattern = re.compile(
                    rf'\[node\s+name="{name_escaped}".*?\](.*?)(?=\[node\s|\[connection|\Z)',
                    re.DOTALL,
                )
                node_match = node_pattern.search(content)
                if node_match:
                    node_block = node_match.group(1)
                    text_match = re.search(r'text\s*=\s*"([^"]*)"', node_block)
                    if text_match:
                        original_text = text_match.group(1)
        except Exception:
            pass

        if not original_text:
            # Fallback: tenta pela chave de tradução (nome do nó como possível chave)
            if ctrl_name in translations_lookup:
                original_text = ctrl_name
            else:
                continue

        # Obtém texto traduzido
        translated_text = translations_lookup.get(original_text, original_text)

        # Estima largura
        estimated_width = _estimate_text_width(translated_text, font_size)

        # Calcula overflow
        if container_w > 0:
            overflow_pct = round((estimated_width - container_w) / container_w * 100, 1)
        else:
            overflow_pct = 0

        if overflow_pct <= 0:
            continue  # Sem overflow

        # Classifica severidade
        if overflow_pct > 150:
            severity = "critical"
        elif overflow_pct > 120:
            severity = "high"
        elif overflow_pct > 100:
            severity = "medium"
        else:
            severity = "low"

        overflows.append({
            "control": ctrl_name,
            "control_type": ctrl_type,
            "control_path": ctrl.get("path", ""),
            "original_text": original_text,
            "translated_text": translated_text,
            "locale": locale,
            "estimated_width": round(estimated_width, 1),
            "container_width": container_w,
            "overflow_pct": overflow_pct,
            "severity": severity,
        })

    return {
        "status": "success",
        "overflows": overflows,
        "total_overflows": len(overflows),
        "locale": locale,
        "scene": scene_path,
        "total_controls_checked": len(visible_controls),
    }


# ══════════════════════════════════════════════════════════════════════
# Op 3 — check_text_contrast
# ══════════════════════════════════════════════════════════════════════

def check_text_contrast(
    scene_path: str,
    project_path: str | None = None,
) -> dict:
    """Verifica contraste texto/fundo em elementos de UI (padrão WCAG).

    Usa capture_ui_snapshot (1.3) para geometria. Tenta obter cores
    de tema do .tscn (theme_override_colors/font_color, theme override
    de Panel/Label). Fallback: assume texto branco sobre fundo escuro
    do tema padrão Godot.

    Args:
        scene_path: Caminho da cena .tscn.
        project_path: Caminho do projeto (auto-detecta se None).

    Returns:
        {"status": "success", "contrasts": [{...}], "total_fails": int,
         "total_warns": int}
    """
    from tools.runtime_ui import capture_ui_snapshot

    proj = _get_proj(project_path)
    snapshot = capture_ui_snapshot(scene_path, str(proj))
    if snapshot.get("status") != "success":
        return snapshot

    controls = snapshot.get("controls", [])
    visible_controls = [c for c in controls if c.get("visible", True)]

    # Cores padrão Godot 4.x: texto claro sobre fundo escuro
    DEFAULT_TEXT_COLOR = (255, 255, 255)       # branco
    DEFAULT_BG_COLOR = (32, 34, 43)            # #20222b (fundo escuro padrão)

    # Tenta ler o .tscn para extrair cores de tema
    scene_colors: dict[str, tuple] = {}  # node_name -> text_color
    scene_bg_colors: dict[str, tuple] = {}  # node_name -> bg_color
    try:
        full_path = proj / scene_path
        if full_path.exists():
            content = full_path.read_text(encoding="utf-8", errors="ignore")
            # Busca font_color (normal ou theme_override)
            color_pattern = re.compile(
                r'\[node\s+name="([^"]+)".*?\].*?'
                r'(?:theme_override_colors/)?font_color\s*=\s*Color\s*\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)',
                re.DOTALL,
            )
            for match in color_pattern.finditer(content):
                name = match.group(1)
                r = int(float(match.group(2)) * 255)
                g = int(float(match.group(3)) * 255)
                b = int(float(match.group(4)) * 255)
                scene_colors[name] = (r, g, b)
    except Exception:
        pass

    contrasts = []
    total_fails = 0
    total_warns = 0

    for ctrl in visible_controls:
        ctrl_type = ctrl.get("type", "")
        if not any(t in ctrl_type for t in ("Label", "Button", "Edit", "Option", "Menu", "Check", "Window")):
            continue

        ctrl_name = ctrl.get("name", "")

        # Obtém cor do texto
        text_rgb = scene_colors.get(ctrl_name, DEFAULT_TEXT_COLOR)
        bg_rgb = scene_bg_colors.get(ctrl_name, DEFAULT_BG_COLOR)

        # Calcula contraste
        ratio = round(_wcag_contrast_ratio(text_rgb, bg_rgb), 2)

        # Classifica (WCAG AA: >=4.5 para texto normal, >=3.0 para texto grande)
        # Aqui usamos o limiar para texto normal como padrão
        if ratio < 3.0:
            status = "fail"
            total_fails += 1
        elif ratio < 4.5:
            status = "warn"
            total_warns += 1
        else:
            status = "pass"

        contrasts.append({
            "control": ctrl_name,
            "control_type": ctrl_type,
            "control_path": ctrl.get("path", ""),
            "text_color": f"#{text_rgb[0]:02x}{text_rgb[1]:02x}{text_rgb[2]:02x}",
            "bg_color": f"#{bg_rgb[0]:02x}{bg_rgb[1]:02x}{bg_rgb[2]:02x}",
            "contrast_ratio": ratio,
            "wcag_level": "AAA" if ratio >= 7.0 else ("AA" if ratio >= 4.5 else "FAIL"),
            "status": status,
        })

    return {
        "status": "success",
        "contrasts": contrasts,
        "total_fails": total_fails,
        "total_warns": total_warns,
        "total_pass": len(contrasts) - total_fails - total_warns,
        "total_controls_checked": len(contrasts),
    }
