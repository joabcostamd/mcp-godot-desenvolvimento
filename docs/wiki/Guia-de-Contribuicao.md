# 📝 Guia de Contribuicao

## Fluxo de Desenvolvimento

1. Identifique a proxima etapa em `ROADMAP_UNIFICADO.md`
2. Verifique `SUTURE_ISSUES.md` para conflitos
3. Implemente EXATAMENTE 1 etapa
4. Audite com `auditar.py` ou `validate_tool_registry_consistency()`
5. Atualize `HANDOFF.md`, `NEXT_STEP.md`, `.roadmap_progress.json`
6. Commit: `feat(agente-X-etapa-Y): descricao em portugues`

## Regras de Ouro

- NUNCA edite arquivos do outro agente
- Respeite `# INTERNAL:` — funcoes usadas por rollups
- 1 commit por etapa
- Auditoria apos cada implementacao
- Conflitos em `SUTURE_ISSUES.md`, nao resolva sozinho

## Ambiente

```bash
# Ativar venv
.\\.venv\\Scripts\\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Rodar testes
python tests/test_code_quality_ops.py
```
