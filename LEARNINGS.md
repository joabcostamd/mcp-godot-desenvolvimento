# 🧠 LEARNINGS.md — Anti-Padrões e Regras de Prevenção

> **Leia este arquivo no início de CADA sessão.**
> **Ordem de leitura**: AUTORUN.md → AGENTS.md → **LEARNINGS.md** → NEXTFEATURES.md
>
> Aqui estão listados apenas os problemas que JÁ ocorreram em produção.
> Para cada um: o padrão que quebra, por que quebra, e a REGRA para nunca mais repetir.
> Isto NÃO é um guia de troubleshooting — é um guia de PREVENÇÃO.

---

## 📋 ÍNDICE RÁPIDO

| # | Regra | Severidade |
|---|-------|-----------|
| R1 | Nunca declare `var` com mesmo nome na mesma função | 🔴 CRÍTICO |
| R2 | Nunca use `:=` com acesso a Dictionary | 🔴 CRÍTICO |
| R3 | Erros de parse são reportados UM por vez | 🟠 ALTO |
| R4 | Game Bridge: código simples primeiro, complexo no .gd | 🟠 ALTO |
| R5 | Porta 9081: sempre matar Godot antes de reiniciar | 🟡 MÉDIO |
| R6 | Cenas: sempre abrir no editor 1 vez após criar .tscn | 🟡 MÉDIO |
| R7 | --headless --quit NÃO testa a cena do jogo | 🟡 MÉDIO |
| R8 | seed() só no _ready(), nunca no _draw() ou _process() | 🟢 BAIXO |
| R9 | Método/propriedade inexistente em classe nativa do Godot | 🟡 MÉDIO |
| R10 | Ciclo declarativo: ler estado → editar → validar → reiniciar → verificar | 🔴 CRÍTICO |
| R11 | Handlers referenciados no _HANDLERS_CACHE DEVEM ser definidos antes do import | 🔴 CRÍTICO |
| R12 | godot --headless --script/--check-only NÃO funciona no Windows 4.7 (ampliado) | 🔴 CRÍTICO |
| R13 | send_bridge_command: sempre testar com jogo RODANDO; ConnectionRefused vira TimeoutError no Windows | 🟠 ALTO |
| R14 | godot_stop_project: verificar nome do processo antes do taskkill (anti-PID-reaproveitado) | 🟠 ALTO |
| R15 | Hooks PostToolUse: validar com PowerShell puro (regex), não depender de venv/Python de outro projeto | 🟡 MÉDIO |
| R16 | socket.create_connection sem listener dá TimeoutError no Windows (não ConnectionRefusedError) | 🟡 MÉDIO |

---

## 🔴 R1 — VARIÁVEL DUPLICADA NO MESMO ESCOPO

### O padrão que quebra
```gdscript
func _draw() -> void:
    var a: float = 0.03 * (5 - ring)   # declaração 1
    # ... 200 linhas depois ...
    var a: float = 0.8 - abs(ly - 300) # declaração 2 → ERRO DE PARSE
```

### Por que quebra
GDScript 4.x **proíbe** redeclarar `var` com o mesmo nome no mesmo escopo de função.
Diferente de escopos aninhados (que GDScript sequer tem para `if`/`for`/`match`),
tudo dentro de uma função é o mesmo escopo léxico.

### O erro exato
```
SCRIPT ERROR: Parse Error: There is already a variable named "a" declared in this scope.
at: GDScript::reload (res://scripts/main.gd:707)
ERROR: Failed to load script "res://scripts/main.gd" with error "Parse error".
```

### Sintoma no jogo
- Tela CINZA após carregar a cena (script não carrega → nada renderiza)
- Game Bridge continua funcionando (autoload separado)

### Impacto real
- **19 variáveis duplicadas** encontradas no `_draw()` do Space Colony TD
- Foram necessárias **3 rodadas** de correção porque o Godot só reporta 1 erro por vez
- Tempo perdido: ~45 minutos de debugging

### ✅ REGRA DE PREVENÇÃO

> **NUNCA reutilize nome de variável dentro da mesma função.**
> Se precisar de uma variável para ângulo/timer/alpha em 5 contextos diferentes,
> dê nomes DESCRITIVOS: `nebula_alpha`, `portal_alpha`, `enemy_angle`, `orbital_t`.
>
> **Prefixos recomendados por contexto no _draw():**
> - Estrelas/nebulosas: `nx`, `ny`, `nebula_r`, `nebula_a`
> - Portal: `portal_center`, `portal_pulse`, `beam_a`
> - Grid: `base_pos`, `cell_color`, `border_color`
> - Torres: `tower_center`, `tower_height`, `tower_color`
> - Inimigos: `epos`, `sz`, `hp_pct`
> - Projéteis: `ppos`, `pcol`
> - Partículas: `pt_pos`, `pt_alpha`
> - Efeitos: `os_beam`, `os_glow_t`, `tw_alpha`
> - HUD: `hx`, `cy`, `buff_y`, `xp_pct`

### ✅ Checklist pré-commit para funções longas (>100 linhas)
1. [ ] `grep -n "var " script.gd | sort -t: -k2` → verificar duplicatas
2. [ ] Se `_draw()` tem +50 variáveis: vale refatorar em funções auxiliares?
3. [ ] Nomes são descritivos? (`a`, `t`, `r` → `alpha`, `turret`, `radius`)

---

## 🔴 R2 — `:=` COM ACESSO A DICTIONARY

### O padrão que quebra
```gdscript
var blocked_pos := enemies[i]["pos"]    # ERRO: Dictionary → Variant
var dir_to_hud := (target - pu["pos"]).normalized()  # ERRO: Dictionary → Variant
```

### Por que quebra
GDScript 4.x usa **inferência de tipo estática** com `:=`.
Quando você acessa um Dictionary (`dict["key"]`), o tipo retornado é `Variant`,
não `Vector2` ou `float`. O compilador **não consegue inferir** o tipo
a partir de um acesso a Dictionary, e `:=` exige tipo inferível.

### O erro exato
```
SCRIPT ERROR: Parse Error: Cannot infer the type of "blocked_pos" variable
because the value doesn't have a set type.
at: GDScript::reload (res://scripts/main.gd:242)
```

### Sintoma no jogo
- IDEM R1: tela cinza, script não carrega

### ✅ REGRA DE PREVENÇÃO

> **NUNCA use `:=` quando o lado direito contém `dict["chave"]`.**
> SEMPRE anote o tipo explicitamente com `: Tipo`.

```gdscript
# ❌ ERRADO
var x := enemies[i]["pos"]
var y := (target - pu["pos"]).normalized()

# ✅ CORRETO
var x: Vector2 = enemies[i]["pos"]
var y: Vector2 = (target - pu["pos"]).normalized()
```

### ✅ Regra complementar
`:=` é seguro APENAS com:
- Construtores explícitos: `var v := Vector2(10, 20)` ✅
- Chamadas de método com tipo de retorno conhecido: `var mp := get_global_mouse_position()` ✅
- Casts: `var col := int(expr)` ✅
- Constantes: `const X := 5` ✅
- **NUNCA** com: `dict[key]`, `array[idx]`, `call()` genérico ❌

---

## 🟠 R3 — ERROS DE PARSE EM CASCATA

### O padrão que quebra
Você corrige 1 erro de parse → compila → aparece outro → corrige → aparece outro → ...

### Por que acontece
O compilador GDScript **para no primeiro erro encontrado** e reporta apenas ele.
Erros subsequentes no mesmo arquivo ficam invisíveis até que o primeiro seja corrigido.
Isso é especialmente perigoso em funções longas com muitos problemas.

### Impacto real
- Space Colony TD: 3 rodadas de fix (pulse → 19 vars → := Dictionary)
- Cada rodada: ~10-15 min (corrigir + compilar + testar + descobrir próximo erro)

### ✅ REGRA DE PREVENÇÃO

> **Após QUALQUER correção de parse, rode o validador preventivo ANTES de compilar.**
>
> O script `scripts/validate_gdscript.py` varre o arquivo e reporta TODOS os
> potenciais problemas de uma vez — sem depender do compilador Godot.

```bash
# Rode isso ANTES de cada compile_test:
python scripts/validate_gdscript.py CAMINHO/DO/ARQUIVO.gd
```

### ✅ Checklist pós-correção de parse
1. [ ] Rodar `validate_gdscript.py` → 0 problemas
2. [ ] `compile_test` → exit code 0
3. [ ] Se `compile_test` falhou: ler o erro, corrigir, VOLTAR AO PASSO 1

---

## 🟠 R4 — GAME BRIDGE COM CÓDIGO COMPLEXO

### O padrão que quebra
```python
# Tentar executar código multi-linha via game bridge
code = """
for i in range(10):
    enemies[i].hp -= 50
    if enemies[i].hp <= 0:
        _kill_enemy(i)
"""
execute_gdscript(code)  # → ERRO DE PARSE
```

### Por que quebra
O Game Bridge tem **dois modos**:
1. **Expression mode**: só aceita expressões simples (`wave`, `enemies.size()`, `1+1`)
2. **Statement mode**: compila como `extends Node\nfunc _execute():\n\t<seu_codigo>`

O Statement mode é frágil com:
- Código multi-linha com indentação complexa
- Acesso a variáveis da cena principal (escopo errado)
- `return` statements (funciona como statement, não como expression)

### Sintoma
- `"Erro de compilacao GDScript: Erro de parse GDScript (codigo 43)"`
- `"Runtime error: Invalid named index 'return' for base type Object"`

### ✅ REGRA DE PREVENÇÃO

> **Game Bridge é para CONSULTAS e INJEÇÕES SIMPLES.**
> Para lógica complexa, SEMPRE edite o arquivo `.gd` e use `smart_restart()`.

| Use Game Bridge para | NÃO use Game Bridge para |
|---------------------|-------------------------|
| `wave` (consultar estado) | `for` loops complexos |
| `enemies.size()` | `if/elif/else` aninhados |
| `_start_next_wave()` (1 chamada) | Múltiplas funções |
| `grid[0][0] = {...}` (1 atribuição) | Criar nós ou cenas |
| `game_over` (boolean) | Código com +3 níveis de indentação |

---

## 🟡 R5 — PORTA 9081 EM USO

### O padrão que quebra
O jogo anterior não foi fechado corretamente → nova instância não consegue abrir a porta.

### Sintoma
```
[GameBridge] ERRO: porta 9081 indisponível.
```
Ou (modo console):
```
[GameBridge] ERRO: porta 9081 indisponível.
```
O jogo abre mas o Game Bridge não funciona → IA não consegue interagir com o jogo.

### ✅ REGRA DE PREVENÇÃO

> **SEMPRE use `smart_restart()` em vez de `run_game()` isolado.**
> `smart_restart()` faz: kill processos antigos → abrir editor → abrir jogo → aguardar bridge.

```python
# ❌ ERRADO
from tools.runtime_ops import run_game
run_game()  # pode falhar se porta já está em uso

# ✅ CORRETO
from tools.runtime_ops import smart_restart
smart_restart()  # sempre funciona, inclui kill + wait + verify
```

### ✅ Se precisar limpar manualmente
```powershell
taskkill /F /IM Godot_v4.7-stable_win64.exe
taskkill /F /IM Godot_v4.7-stable_win64_console.exe
```

---

## 🟡 R6 — FORMATO DE CENA GODOT 3 vs 4

### O padrão que quebra
Criar `.tscn` com `format=2` (Godot 3) e o Godot 4 não consegue resolver UIDs.

### Sintoma
- Referências a recursos quebradas (`[ext_resource]` sem UID)
- Cena carrega mas nós perdem scripts ou texturas

### ✅ REGRA DE PREVENÇÃO

> **Após criar QUALQUER `.tscn` via MCP, abra o projeto no Godot Editor 1 vez.**
> O editor auto-converte `format=2` → `format=3` e gera UIDs corretos.
>
> **OU** use `create_scene` com o editor aberto (mcp_addon na porta 9082 fará a
> conversão automaticamente).

### ✅ Verificação rápida
```bash
head -1 cena.tscn
# Deve ser: [gd_scene load_steps=N format=3 uid="uid://..."]
# Se for:   [gd_scene load_steps=N format=2]  → PROBLEMA
```

---

## 🟡 R7 — `--headless --quit` NÃO TESTA A CENA DO JOGO

### O padrão que quebra
O projeto tem `main_scene="scenes/main_menu.tscn"`. O `--headless --quit` carrega
o menu, não o jogo. Se `main.gd` tem erros de parse, o compile test passa LIMPO
porque o script nunca é carregado.

### Impacto real
- 3 correções de parse foram necessárias porque o compile test não detectou
- Usuário via tela cinza → IA dizia "compilou limpo" → frustração

### ✅ REGRA DE PREVENÇÃO

> **Sempre que alterar `main.gd`, teste com a cena ESPECÍFICA:**
>
> ```bash
> godot --headless --path PROJETO res://scenes/main.tscn --quit
> ```
>
> NUNCA confie apenas no `compile_test()` genérico para scripts de cena.

### ✅ Script de teste completo
```python
from tools.runtime_ops import _do_compile

# Teste genérico (menu)
_do_compile(proj, godot, timeout)

# Teste específico (cena do jogo)
import subprocess
result = subprocess.run(
    [godot, "--headless", "--path", str(proj), "res://scenes/main.tscn", "--quit"],
    capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL
)
if result.returncode != 0 or "PARSE ERROR" in result.stderr or "SCRIPT ERROR" in result.stderr:
    print(f"ERRO NA CENA PRINCIPAL: {result.stderr}")
```

---

## 🟢 R8 — seed() NO LUGAR ERRADO

### O padrão que quebra
```gdscript
func _draw() -> void:
    seed(42)  # ❌ seed a cada frame!
    for i in range(60):
        var sx = randf() * 1280  # estrelas piscando loucamente
```

### Por que quebra
`seed()` no `_draw()` faz o gerador aleatório reiniciar a cada frame (60×/segundo).
Isso causa flickering visual intenso em estrelas e partículas.

### ✅ REGRA DE PREVENÇÃO

> **`seed(42)` APENAS no `_ready()`. NUNCA no `_draw()` ou `_process()`.**

```gdscript
func _ready() -> void:
    seed(42)  # ✅ uma vez, na inicialização
    # ...
```

---

## � R9 — MÉTODO/PROPRIEDADE INEXISTENTE EM CLASSE NATIVA

### O padrão que quebra
```gdscript
var sprite: Sprite2D
func _ready() -> void:
    sprite.set_textur(null)        # ❌ método não existe (é set_texture)
    sprite.metodo_que_nao_existe() # ❌ totalmente inventado
```

### Por que quebra
Erros de digitação em nomes de métodos de classes nativas do Godot
(`Sprite2D`, `Label`, `Timer`, etc.) só são descobertos em runtime,
desperdiçando um ciclo completo de compile-test-fix.

### Sintoma no jogo
- `Invalid call. Nonexistent function 'set_textur' in base 'Sprite2D'`
- Só aparece quando o Godot executa aquela linha específica

### ✅ REGRA DE PREVENÇÃO

> **O validador `validate_gdscript.py` (R9) verifica automaticamente se todo método**
> **chamado em variável com tipo Godot nativo EXPLÍCITO existe naquela classe**
> **ou em qualquer ancestral (herança completa).**

```bash
# Roda automaticamente junto com R1 e R2:
python scripts/validate_gdscript.py main.gd
```

### ⚠️ Limitações conscientes (NÃO reporta erro para):
- Variáveis sem tipo explícito (`var x = ...`)
- Tipos customizados do usuário (`class_name MeuScript`)
- `get_node()` sem cast (retorna `Node` genérico)
- Chamadas dinâmicas (`call()`, `callv()`, sinais por string)
- Tipos builtin (`Array`, `Vector2`, `Dictionary`, `int`, `String`)
- **Sinais nativos** (`timer.timeout`, `button.pressed`) — reconhecidos via `is_valid_signal()`, acesso legítimo

### ⚠️ Falsos positivos conhecidos e aceitos (NÃO são bugs da R9):
- **Type narrowing**: `event.keycode` em `InputEvent` — o código usa `if event is InputEventKey` antes, mas o validador não acompanha refinamento de tipo por `is`
- **Scripts customizados**: `_dock.setup()` em variável `Control` — o tipo declarado é a classe base, mas o objeto real é uma subclasse com métodos extras (inclusive com guarda `has_method()`)

### 🎯 Cobertura real
- ✅ `sprite.set_texture()` → existe em Sprite2D → OK
- ✅ `sprite.queue_free()` → herdado de Object → OK
- ❌ `sprite.metodo_falso()` → não existe → **REPORTADO**
- ❌ `sprite.set_textur()` → não existe, sugere: `set_texture` → **REPORTADO COM SUGESTÃO**

## 🔴 R10 — CICLO DECLARATIVO: LER ESTADO → EDITAR → VALIDAR → REINICIAR → VERIFICAR

### O padrão que quebra
A IA edita um arquivo `.gd` ou `.tscn` baseada no que **acha** que existe
no projeto, sem confirmar o estado real. O resultado é dessincronia:
nomes de nós errados, propriedades que mudaram, código que referencia
variáveis que não existem mais. Cada erro desses custa 1 ciclo completo
de compile-test-fix (~30-60s), e em cascata podem ser 3-5 ciclos.

### Por que acontece
- A IA não "vê" o projeto — ela trabalha com uma representação mental
  que fica desatualizada após cada mudança.
- Não existe instrução formal dizendo para reler o estado antes de editar.
- O ciclo "editar → torcer para compilar" é mais rápido no curto prazo
  mas gera mais retrabalho.

### ✅ REGRA DE PREVENÇÃO — ORDEM OBRIGATÓRIA DO CICLO

> **Para toda mudança que NÃO for greenfield (projeto/cena nova do zero),
> siga esta ordem. Não pule passos.**

```
1. LER ESTADO (se a mudança depende do que já existe)
   ├── analyze_game_structure()     → métricas gerais do projeto
   ├── load_scene_tree("cena.tscn")  → árvore de nós e propriedades
   └── read_file("script.gd", start, end) → trecho específico

2. EDITAR ARQUIVOS (abordagem declarativa — editar .gd/.tscn direto)
   ├── write_file / set_node_property / generate_gdscript
   └── NUNCA mandar código complexo pelo game bridge (R4)

3. VALIDAR (ANTES de compilar no Godot)
   └── python scripts/validate_gdscript.py <arquivo.gd>

4. REINICIAR (nunca run_game() isolado — R5)
   └── smart_restart()  # kill + compile + start + bridge (~10-15s)

5. VERIFICAR (não assumir sucesso)
   ├── read_console_output()        → erros/warnings do Godot
   └── get_scene_tree() via bridge   → confirmar que a cena carregou
```

### ⚡ Quando aplicar vs. quando pular

| Situação | Aplicar ciclo? |
|----------|:-------------:|
| Adicionar lógica a nó/scene existente | ✅ COMPLETO |
| Corrigir bug em código existente | ✅ COMPLETO |
| Mudar propriedade de cena existente | ✅ COMPLETO |
| Criar projeto NOVO do zero | ❌ Pular passo 1 |
| Criar cena NOVA (ainda não referenciada) | ❌ Pular passo 1 |
| Adicionar torre/inimigo NOVO (sem depender do grid) | ⚠️ Passo 1 leve (só analyze) |

### 📊 Motivação (1 frase)
Reduzir ciclos de tentativa-erro por dessincronia entre o modelo mental da IA e o estado real do projeto — cada ciclo evitado economiza ~30-60s.

## �📋 CHECKLIST DE INÍCIO DE SESSÃO

Antes de começar a implementar features, execute:

```bash
# 1. Validar o GDScript atual
python scripts/validate_gdscript.py CAMINHO/DO/main.gd

# 2. Rodar compile test com a cena correta
godot --headless --path PROJETO res://scenes/main.tscn --quit

# 3. Verificar se não há processos Godot zumbis
taskkill /F /IM Godot*.exe 2>$null

# 4. Iniciar ambiente limpo
python -c "from tools.runtime_ops import smart_restart; smart_restart()"
```

---

## 🔴 R11 — HANDLERS REFERENCIADOS MAS NÃO DEFINIDOS (NameError)

### O padrão que quebra
```python
# Em _build_handlers():
"godot_screenshot": _handle_godot_screenshot,  # ← NameError se não definida antes!

# ... 300 linhas depois, a função NUNCA foi escrita
```

### Por que quebra
O `_build_handlers()` referencia funções que precisam ser definidas ANTES do dicionário ser construído (em module-level ou como funções acima do dict no mesmo arquivo). Se a função não existe no namespace quando o dict é avaliado, `NameError`.

### ✅ REGRA DE PREVENÇÃO
Sempre verificar: `grep "_handle_NOME" server.py` deve retornar PELO MENOS 2 ocorrências (1 no dict, 1 na definição). Nunca commitar com apenas 1 match.

---

## 🔴 R12 — GODOT --HEADLESS NÃO FUNCIONA NO WINDOWS 4.7 (AMPLIADO 2026-07-12)

### O padrão que quebra
```bash
# AMBOS falham no Windows Godot 4.7:
godot --headless --script check.gd              # stdout/stderr/FileAccess/exit code vazios
godot --editor --headless --check-only --path P  # timeout >30s em qualquer projeto
```

### Por que quebra
No Windows Godot 4.7:
- `--headless --script`: stdout/stderr vazios, FileAccess.WRITE não cria arquivos, exit code ignorado
- `--headless --check-only`: trava indefinidamente (testado em 3 tipos de projeto: minimal, Star Colony real, completo com addons/scenes/scripts)

### Impacto
- `compile_test` não pode usar `--headless --script` para validação
- `safe_write_gdscript` não pode confiar na validação Godot — depende apenas de sandbox + sintaxe local

### ✅ REGRA DE PREVENÇÃO
- **`tentar_checagem_godot` deve ser `false` no config.json** (default desde 2026-07-12)
- A checagem Godot foi desligada por padrão
- Para religar quando versão futura corrigir: `"tentar_checagem_godot": true`
- Usar LSP bridge (:6005) ou runtime bridge (:8790) para validação real

---

## 🟠 R13 — send_bridge_command EXIGE JOGO RODANDO

### O padrão que quebra
```python
send_bridge_command({"cmd": "runtime_info"})  # Jogo parado → hang de 5s
```

### Por que quebra
No Windows, `socket.create_connection` para porta sem listener dá `TimeoutError` (5s), não `ConnectionRefusedError`. O script parece "travado".

### ✅ REGRA DE PREVENÇÃO
Sempre usar `godot_wait_for_bridge(timeout_sec=15)` antes de chamar send_bridge_command. Ou capturar explicitamente `TimeoutError` + `ConnectionRefusedError` + `OSError`.

---

## 🟠 R14 — GODOT_STOP_PROJECT: VERIFICAR NOME DO PROCESSO

### O padrão que quebra
```python
taskkill /F /PID 1234  # PID pode ter sido reaproveitado pelo Windows!
```

### Por que quebra
Se o Godot já morreu sozinho e o Windows reaproveitou o PID para outro programa (ex: notepad), `taskkill /F` mataria um processo inocente.

### ✅ REGRA DE PREVENÇÃO
Antes do `taskkill`, verificar `tasklist /FI "PID eq X" /FO CSV`: o nome do executável deve conter "Godot". Se não, recusar com erro.

---

## 🟡 R15 — HOOKS POSTTOOLUSE: NÃO DEPENDER DE VENV EXTERNO

### O padrão que quebra
```powershell
# Hook no NUCLEO referencia Python/venv do mcp-godot-desenvolvimento
$PYTHON = "C:\...\mcp-godot-desenvolvimento\.venv\Scripts\python.exe"
```

### Por que quebra
Se o venv for recriado, movido, ou o caminho mudar entre máquinas, o hook quebra silenciosamente.

### ✅ REGRA DE PREVENÇÃO
Hooks devem ser autocontidos: PowerShell puro (regex) ou binários do sistema (Godot no PATH/Godot_PATH). Zero referências cruzadas entre projetos.

---

## 🟡 R16 — TIMEOUTERROR VS CONNECTIONREFUSEDERROR NO WINDOWS

### O padrão que quebra
```python
except ConnectionRefusedError:  # ← NUNCA dispara no Windows para localhost!
```

### Por que quebra
No Windows, `socket.create_connection(('127.0.0.1', PORT))` com porta fechada gera `TimeoutError` (subclasse de `OSError`), não `ConnectionRefusedError`.

### ✅ REGRA DE PREVENÇÃO
Sempre capturar `(ConnectionRefusedError, socket.timeout, OSError)` juntos, ou usar `except Exception` com mensagem genérica de "bridge unavailable".

---

> **Última atualização**: 2026-07-12 — Sessão 3 (Patches 12-18)
> **Baseado em**: 16 bugs/limitações reais encontrados no desenvolvimento do MCP Godot Agent
> **Próximo passo**: Automatizar o máximo possível destas verificações
