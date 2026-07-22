# InputManager — Gerenciador de Input com Rebinding

> Node | Godot 4.7 | v1.0.0 | Grupo: SISTEMA

## 📝 Descrição

Node que gerencia rebinding de input em runtime. Permite reassociar
teclas/botões a ações do InputMap, detecta tipo de dispositivo e
salva/carrega bindings via ConfigFile. Essencial para jogos com
controles customizáveis.

## 🎯 Quando Usar

- Menu de configuração de controles
- Suporte a múltiplos dispositivos (teclado, gamepad, touch)
- Persistência de preferências de input do jogador

## ⚡ Quick Start

```gdscript
var im := InputManager.new()
add_child(im)

# Detectar dispositivo
im.device_changed.connect(func(device): print("Usando: ", device))

# Rebinding
var event := InputEventKey.new()
event.keycode = KEY_SPACE
im.rebind_action("ui_accept", event)

# Salvar/carregar
im.save_bindings()
im.load_bindings()
```

## 🔧 Propriedades

| Nome | Tipo | Default | Descrição |
|------|------|---------|-----------|
| `bindings_path` | String | `user://input_bindings.cfg` | Arquivo de bindings |

## 📡 Sinais

| Nome | Params | Quando Emitido |
|------|--------|----------------|
| `device_changed` | `device_type: String` | Dispositivo muda |
| `action_rebound` | `action_name: String, event: InputEvent` | Ação reassociada |

## ⚠️ Edge Cases

| Cenário | Comportamento |
|---------|---------------|
| `rebind_action` com ação inexistente | Retorna false |
| `rebind_action` com evento null | Retorna false |
| `load_bindings` com arquivo inexistente | Retorna false |
| Dispositivo igual não re-emite `device_changed` | PADRÃO 10 |

## ✅ Cobertura de Testes

- `test_detect_keyboard` — Detecta teclado
- `test_detect_gamepad` — Detecta gamepad
- `test_detect_touch` — Detecta touch
- `test_device_changed_signal` — Sinal device_changed
- `test_device_changed_no_duplicate` — PADRÃO 10
- `test_rebind_action` — Rebinding funcional
- `test_rebind_nonexistent_action` — Ação inexistente
- `test_action_rebound_signal` — Sinal action_rebound
- `test_save_and_load_bindings` — Roundtrip save/load
- `test_load_nonexistent_file` — Arquivo inexistente
- `test_rebind_null_event` — Evento null
- `test_reset_action` — Reset individual
- `test_reset_all` — Reset global

## 📚 Fonte

- Godot 4.7 ClassDB: InputMap, InputEvent, ConfigFile
- Nodot: InputManager component
