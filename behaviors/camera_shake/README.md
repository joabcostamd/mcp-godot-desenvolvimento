# CameraShake — Tremor Sinusoidal de Câmera

> Node | Godot 4.7 | v1.0.0 | Grupo: CÂMERA

## 📝 Descrição

Node que aplica tremor sinusoidal periódico à Camera2D. Diferente de
ScreenShake (aleatório), este usa onda senoidal com frequência configurável
para vibração controlada. Ideal para terremotos, vibração de motor, passos
pesados e outros efeitos de oscilação rítmica.

**Diferença vs ScreenShake (#40):** ScreenShake usa `randf_range()` para tremor
caótico (explosões). CameraShake usa `sin()` para oscilação suave e periódica.

## 🎯 Quando Usar

- Terremoto / tremor de terra
- Vibração de motor ou máquina
- Passos de boss gigante
- Qualquer efeito de oscilação rítmica na câmera

## ⚡ Quick Start

```gdscript
# Adicionar como filho de Camera2D
var shake := CameraShake.new()
$Camera2D.add_child(shake)

# Disparar tremor
shake.amplitude = 8.0
shake.frequency = 15.0
shake.duration = 1.5
shake.trigger()

# Ou com override de amplitude
shake.trigger(20.0)
```

## 🔧 Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `amplitude` | float | 0.1–100 | 5.0 | Intensidade (px) |
| `frequency` | float | 0.5–60 | 10.0 | Frequência (Hz) |
| `duration` | float | 0.05–10 | 0.5 | Duração (s) |
| `decay` | float | 0.0–1.0 | 0.8 | Decaimento (0=linear, 1=sem) |
| `direction` | Vector2 | — | (1,1) | Eixo do tremor |

## 📡 Sinais

| Nome | Params | Quando Emitido |
|------|--------|----------------|
| `shake_started` | — | Ao iniciar tremor |
| `shake_finished` | — | Ao terminar (duração ou stop) |

## ⚠️ Edge Cases

| Cenário | Comportamento |
|---------|---------------|
| `trigger()` durante shake ativo | Ignorado (PADRÃO 10) |
| `direction = (0,0)` | Normalizado para (1,1) |
| Sem Camera2D no parent | Shake ativo mas sem efeito visual |
| `stop()` com shake inativo | No-op |

## ✅ Cobertura de Testes

- `test_trigger_starts_shake` — Trigger ativa o shake
- `test_trigger_guards_duplicate` — PADRÃO 10: duplo trigger ignorado
- `test_stop_restores_offset` — Stop restaura offset original
- `test_stop_when_inactive` — Stop inativo é no-op
- `test_shake_started_signal` — Sinal shake_started
- `test_shake_finished_signal_on_duration` — Sinal ao expirar duração
- `test_shake_finished_signal_on_stop` — Sinal ao chamar stop()
- `test_offset_is_sinusoidal` — Verifica padrão senoidal (max→0→min)
- `test_decay_reduces_amplitude` — Decaimento reduz amplitude
- `test_direction_normalized` — Direção é normalizada
- `test_direction_zero_defaults` — Direção zero = fallback
- `test_trigger_without_camera` — Trigger sem câmera
- `test_amplitude_override` — Override de amplitude

## 📚 Fonte

- Godot 4.7 ClassDB: Camera2D, Node._process, TAU, sin()
- Juicee: Shake components (99 efeitos)
- Shaker: 7 shake types
