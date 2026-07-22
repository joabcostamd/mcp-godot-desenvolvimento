# CharacterCreator — Criador de Personagem Customizável

> Control | Godot 4.7 | v1.0.0 | Grupo: PERSONAGEM

## 📝 Descrição

Control que gerencia partes customizáveis de personagem (cabelo, olhos, corpo, etc.)
com opções por parte e paleta de cores. Suporta presets salvos via ConfigFile,
integrando com SaveLoad sibling para diretório de saves. Ideal para telas de
criação de personagem em RPGs e jogos com avatar customizável.

## 🎯 Quando Usar

- Tela de criação de personagem (RPG, MMO, life sim)
- Seleção de avatar/skin
- Editor de aparência in-game (barbeiro, vestiário)
- Qualquer sistema que precise de partes customizáveis com persistência

## ⚡ Quick Start

```gdscript
var creator := CharacterCreator.new()
add_child(creator)

# Registrar partes customizáveis
creator.add_part("hair", ["hair_01", "hair_02", "hair_03", "hair_04"])
creator.add_part("eyes", ["eyes_01", "eyes_02"])
creator.add_part("body", ["body_male", "body_female"])

# Alterar opções
creator.set_part_option("hair", 2)   # seleciona hair_03
creator.set_part_color("hair", Color.RED)

# Salvar/carregar presets
creator.save_preset("meu_guerreiro")
creator.load_preset("meu_guerreiro")

# Obter dados para aplicar ao modelo
var data := creator.get_character_data()
# Ex: data["hair"]["option"] = 2, data["hair"]["color"] = Color.RED
```

## 🔧 Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `preset_category` | String | — | `"default"` | Categoria para agrupar presets (ex: player, npc) |
| `color_palette` | PackedColorArray | — | 8 cores básicas | Paleta de cores disponíveis |

## 📡 Sinais

| Nome | Params | Quando Emitido |
|------|--------|----------------|
| `part_changed` | `part_name: String` | Opção ou cor de uma parte alterada |
| `saved` | `preset_name: String` | Preset salvo com sucesso |
| `loaded` | `preset_name: String` | Preset carregado com sucesso |

## 🔗 Dependências

- `save_load` (recomendado) — se presente como irmão, presets usam o mesmo diretório
  de saves para consistência. Sem SaveLoad, presets são salvos em
  `user://character_presets/{category}/`.

## 🧩 Exemplo de Composição

```
CharacterBody2D (Player)
  ├── SaveLoad
  ├── CharacterCreator
  │     hair: hair_03 (RED)
  │     eyes: eyes_01 (BLUE)
  │     body: body_male (WHITE)
  ├── Sprite2D (atualizado via part_changed)
  └── Health
```

## ⚠️ Edge Cases

| Cenário | Comportamento |
|---------|---------------|
| `set_part_option("ghost", 0)` | No-op silencioso. Retorna -1 em get. |
| `add_part("hair")` duplicado | push_warning, retorna false, original preservado |
| `color_palette` vazio | Setter força `[Color.WHITE]` como fallback |
| `save_preset("")` | Retorna false |
| `load_preset("inexistente")` | Retorna false |
| `load_character_data` com partes desconhecidas | Partes desconhecidas ignoradas silenciosamente |
| `randomize_character` com 0 partes | No-op, sem crash |
| `set_part_option` com mesmo valor | No-op, não emite `part_changed` |
| Sem SaveLoad irmão | Presets funcionam normalmente com diretório próprio |

## ✅ Cobertura de Testes

- `test_add_part_and_set_option` — Adição e seleção de opção
- `test_add_part_empty_options` — Parte sem opções (current=-1)
- `test_add_duplicate_part` — Duplicata rejeitada
- `test_remove_part` — Remoção de parte
- `test_set_option_clamped` — Índices fora do range são clampados
- `test_set_part_color` — Definição de cor
- `test_part_color_nonexistent` — Cor de parte inexistente
- `test_part_changed_signal_on_option` — Sinal ao mudar opção
- `test_part_changed_signal_on_color` — Sinal ao mudar cor
- `test_part_changed_no_duplicate_signal` — PADRÃO 10: sem sinal duplicado
- `test_get_character_data` — Exportação de dados
- `test_load_character_data` — Importação de dados
- `test_load_character_data_empty` — Importação vazia
- `test_preset_save_and_load` — Roundtrip save/load
- `test_preset_signal` — Sinais saved/loaded
- `test_preset_nonexistent` — Load de preset inexistente
- `test_delete_nonexistent_preset` — Delete de preset inexistente
- `test_get_preset_names` — Listagem de presets
- `test_randomize_character` — Aleatorização
- `test_randomize_empty_parts` — Aleatorização com 0 partes
- `test_reset_to_defaults` — Reset para defaults
- `test_nonexistent_part_option` — Acesso a parte inexistente
- `test_nonexistent_part_options_array` — Opções de parte inexistente
- `test_empty_part_name` — Nome vazio rejeitado
- `test_save_preset_empty_name` — Save com nome vazio
- `test_load_preset_empty_name` — Load com nome vazio
- `test_color_palette_fallback` — Fallback paleta vazia
- `test_set_part_option_noop` — PADRÃO 10: no-op guard

## 📚 Fonte

- Godot 4.7 ClassDB: Control, ConfigFile, DirAccess, FileAccess
- Pattern: RPG character creation (Skyrim, Baldur's Gate 3, Elden Ring)
- SaveLoad integration pattern do próprio projeto
