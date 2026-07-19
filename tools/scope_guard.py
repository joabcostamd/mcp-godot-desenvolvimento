"""scope_guard.py — Guardiao de escopo anti-creep (Fatia 1.13).

Classifica sugestoes de features contra GDD, fase atual e milestones.
Responde com classificacao + pergunta consciente. Agressivo no corte.

Tambem trava geracao de arte final antes da mecanica estar fechada
(fase < CONTEUDO).

Uso:
    from tools.scope_guard import scope_check, art_gate_check
    result = scope_check("adicionar multiplayer online")
    # -> {"classificacao": "fora_escopo", ...}
"""

import re as _re
from dataclasses import dataclass, asdict


@dataclass
class ScopeVerdict:
    """Resultado da verificacao de escopo."""

    feature: str
    classificacao: str  # "mvp" | "pos_mvp" | "fora_escopo"
    justificativa: str
    pergunta: str  # pergunta para o humano decidir
    fase_atual: str = ""
    gdd_match: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


# Keywords que indicam escopo expansivo (fora do MVP)
FORA_ESCOPO_KEYWORDS: list[tuple[str, str]] = [
    ("multiplayer|online|coop|pvp|network|servidor", "Multiplayer/online"),
    ("\bia\b|inteligencia artificial|machine learning|ml|neural", "IA avancada"),
    ("procedural|infinito|gerado|random.*map", "Geracao procedural"),
    ("fisica.*realista|ragdoll|simulacao.*fisica", "Fisica complexa"),
    ("editor.*nivel|level.*editor|map.*editor|sandbox", "Editor de niveis"),
    ("save.*cloud|leaderboard|ranking|achievement|steam", "Integracao Steam/Cloud"),
    ("\bvr\b|realidade virtual|\bar\b|oculus|quest", "VR/AR"),
    ("localizacao|traducao|i18n|l10n|multi.*lingua", "Localizacao/i18n"),
    ("mod|modding|api.*publica|script.*externo", "Suporte a mods"),
    ("cutscene|cinematic|filme|animacao.*complexa", "Cutscenes complexas"),
    ("ia.*inimigo.*complexa|comportamento.*emergente|btree", "IA de inimigo avancada"),
]

# Keywords que indicam feature de MVP (core loop)
MVP_KEYWORDS: list[tuple[str, str]] = [
    ("torre|tower|turret|defesa|colocar.*arma", "Torres/defesas"),
    ("inimigo|enemy|wave|spawn|horda", "Inimigos/waves"),
    ("upgrade|melhoria|evoluir|nivel.*torre", "Upgrades"),
    ("recurso|gold|moeda|dinheiro|coletar", "Recursos/coleta"),
    ("grid|grade|mapa.*grid|posicionar", "Grid/posicionamento"),
    ("vida|hp|health|dano|damage|ataque", "Combate basico"),
    ("menu|hud|ui|interface|botao|tela.*titulo", "UI/HUD"),
    ("fase|level|mapa.*fixo|cena.*jogo", "Fases/mapas"),
    ("colisao|hitbox|hit.*box|deteccao", "Colisao basica"),
    ("save|salvar|carregar|load|persistencia", "Save/Load basico"),
    ("som|audio|musica|sfx|efeito.*sonoro", "Audio basico"),
    ("controle|input|teclado|mouse|gamepad", "Controles/input"),
]


class ScopeGuard:
    """Guardiao de escopo — classifica e pergunta."""

    def check(
        self, feature_desc: str, project_path: str | None = None
    ) -> dict:
        """Classifica uma sugestao de feature.

        Args:
            feature_desc: Descricao da feature sugerida
            project_path: Caminho do projeto (opcional)

        Returns:
            ScopeVerdict como dict
        """
        feature_lower = (feature_desc or "").lower().strip()

        if not feature_lower:
            return ScopeVerdict(
                feature=str(feature_desc),
                classificacao="fora_escopo",
                justificativa="Feature vazia ou nula.",
                pergunta="Descreva a feature para classificacao.",
            ).to_dict()

        # 1. Obter contexto do projeto
        fase = self._get_current_phase(project_path)
        brief = self._get_project_brief(project_path)

        # 2. Checar contra keywords
        fora = self._match_keywords(feature_lower, FORA_ESCOPO_KEYWORDS)
        mvp = self._match_keywords(feature_lower, MVP_KEYWORDS)

        # 3. Decidir classificacao
        if fora and not mvp:
            return ScopeVerdict(
                feature=feature_desc,
                classificacao="fora_escopo",
                justificativa=(
                    f"Feature se encaixa em '{fora}' — categoria tipicamente "
                    f"fora do MVP. Fase atual: {fase}."
                ),
                pergunta=(
                    f"Esta feature ({fora}) parece fora do escopo do MVP. "
                    f"Deseja adicionar ao roadmap (pos-MVP) ou fazer agora "
                    f"mesmo assim?"
                ),
                fase_atual=fase,
                gdd_match=False,
            ).to_dict()

        if mvp:
            return ScopeVerdict(
                feature=feature_desc,
                classificacao="mvp",
                justificativa=(
                    f"Feature se encaixa em '{mvp}' — alinhada com o "
                    f"core loop do jogo. Fase atual: {fase}."
                ),
                pergunta=(
                    f"Feature MVP detectada ({mvp}). Prosseguir com "
                    f"implementacao?"
                ),
                fase_atual=fase,
                gdd_match=True,
            ).to_dict()

        # Ambiguo — nao bate em nenhuma keyword forte
        return ScopeVerdict(
            feature=feature_desc,
            classificacao="pos_mvp",
            justificativa=(
                f"Feature nao classificada como MVP ou fora de escopo. "
                f"Fase atual: {fase}. Genero: {brief.get('genre', '?')}."
            ),
            pergunta=(
                f"Esta feature nao parece essencial para o MVP mas tambem "
                f"nao e claramente fora de escopo. Classificar como pos-MVP "
                f"ou promover para MVP?"
            ),
            fase_atual=fase,
            gdd_match=False,
        ).to_dict()

    def art_gate(self, project_path: str | None = None) -> dict:
        """Trava geracao de arte final antes da mecanica estar fechada.

        Returns:
            {"permitido": bool, "motivo": str}
        """
        fase = self._get_current_phase(project_path)
        fases_com_arte = {"CONTEUDO", "POLIMENTO", "PRONTO_PARA_LANCAR"}

        if fase in fases_com_arte:
            return {
                "permitido": True,
                "motivo": f"Fase {fase} permite geracao de arte final.",
                "fase_atual": fase,
            }
        else:
            return {
                "permitido": False,
                "motivo": (
                    f"Fase {fase} nao permite arte final. "
                    f"A mecanica precisa estar fechada primeiro (fase CONTEUDO). "
                    f"Use placeholders visuais por enquanto."
                ),
                "fase_atual": fase,
                "sugestao": "Use asset_manage com type='placeholder' para arte temporaria.",
            }

    # ── Helpers ────────────────────────────────────────────────

    def _match_keywords(self, text: str, patterns: list) -> str | None:
        """Tenta casar texto contra lista de (regex, label)."""
        for regex, label in patterns:
            if _re.search(regex, text):
                return label
        return None

    def _get_current_phase(self, project_path: str | None) -> str:
        """Obtem a fase atual do projeto."""
        try:
            from tools.phase_ops import get_current_phase
            result = get_current_phase()
            if result.get("status") == "success":
                return result.get("phase", "IDEIA")
        except Exception:
            pass
        return "IDEIA"

    def _get_project_brief(self, project_path: str | None) -> dict:
        """Obtem o project brief (genero, estilo)."""
        try:
            from tools.project_brief_ops import get_project_brief
            result = get_project_brief()
            if result.get("status") == "success":
                return result.get("brief") or {}
        except Exception:
            pass
        return {}


# ── Singleton ──────────────────────────────────────────────────────

_guard: ScopeGuard | None = None


def get_scope_guard() -> ScopeGuard:
    global _guard
    if _guard is None:
        _guard = ScopeGuard()
    return _guard


def scope_check(feature_desc: str, project_path: str | None = None) -> dict:
    """Interface publica — classifica uma sugestao de feature."""
    return get_scope_guard().check(feature_desc, project_path)


def art_gate_check(project_path: str | None = None) -> dict:
    """Interface publica — verifica se pode gerar arte final."""
    return get_scope_guard().art_gate(project_path)
