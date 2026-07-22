# CameraFramed — Câmera com Dead Zone

> Node | Godot 4.7 | v1.0.0 | Grupo: CÂMERA

## 📝 Descrição

Node que implementa câmera com dead zone (zona morta). Inspirado no
Phantom Camera "Framed". A câmera só segue o alvo quando ele sai da
dead zone central. Movimento suave com damping na soft zone.

## 🎯 Quando Usar

- Jogos de plataforma (câmera não-rígida)
- Jogos de ação com movimento rápido
- Qualquer cena onde câmera 100% grudada no player é indesejável

## ⚡ Quick Start

```gdscript
# Adicionar como filho de Camera2D
var framed := CameraFramed.new()
$Camera2D.add_child(framed)

# Definir alvo
framed.target = $Player

# Configurar zonas
framed.dead_zone = Vector2(120, 80)
framed.soft_zone = Vector2(60, 40)
framed.damping = 0.08
```

## 🔧 Propriedades

| Nome | Tipo | Range | Default | Descrição |
|------|------|-------|---------|-----------|
| `dead_zone` | Vector2 | 10–2000 | (100,60) | Zona morta (target livre) |
| `soft_zone` | Vector2 | 0–1000 | (80,50) | Margem de damping |
| `damping` | float | 0.01–1.0 | 0.1 | Suavização do movimento |
| `target` | Node2D | — | null | Alvo a seguir |

## 📡 Sinais

| Nome | Params | Quando Emitido |
|------|--------|----------------|
| `target_entered_dead_zone` | — | Target entra na dead zone |

## ⚠️ Edge Cases

| Cenário | Comportamento |
|---------|---------------|
| Sem Camera2D no parent | No-op, sem crash |
| Sem target definido | No-op, sem crash |
| Target dentro da dead zone | Câmera não move |
| Soft zone = (0,0) | Snap imediato ao sair da dead zone |

## ✅ Cobertura de Testes

- `test_target_in_dead_zone_no_camera_movement` — Câmera parada
- `test_target_outside_dead_zone_moves_camera` — Câmera segue
- `test_is_target_in_dead_zone` — Verificação de dead zone
- `test_target_entered_dead_zone_signal` — Sinal ao entrar
- `test_damping_controls_speed` — Damping afeta velocidade
- `test_no_target_no_crash` — Sem target, sem crash
- `test_no_camera_no_crash` — Sem câmera, sem crash

## 📚 Fonte

- Phantom Camera: Framed component (14 camera components)
- Godot 4.7 ClassDB: Camera2D, Node._process
