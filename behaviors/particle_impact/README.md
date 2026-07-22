# Particle Impact

Emissor de partículas de impacto one-shot. Emite explosões, faíscas ou poeira via `emit(position, color)`. Usa `particle_scene` customizada ou cria GPUParticles2D padrão. Auto-limpeza após `finished`.

**Parâmetros:** `particle_scene` (PackedScene), `default_count`, `spread` (px), `auto_free`.

**Uso:** `emit(hit_position, Color.ORANGE)` — emite `particles_emitted(count)`.

**Fontes:** Godot 4.7 ClassDB (`GPUParticles2D`, `CpuParticles2D`, `ParticleProcessMaterial`), padrão universal one-shot particles.
