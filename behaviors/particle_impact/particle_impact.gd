## ParticleImpact — Partículas de Impacto | Godot 4.7 Style Guide compliant.
##
## Emite partículas one-shot (explosão, faísca, poeira) na posição desejada.
## emit(position, color) instancia particle_scene e auto-limpa após finished.
##
## @behavior: particle_impact
## @genres: generic
## @tutorial: behaviors/particle_impact/README.md

@tool
class_name ParticleImpact
extends Node2D

@export var particle_scene: PackedScene = null
@export var default_count: int = 10: set(v): default_count = clampi(v, 1, 100)
@export var spread: float = 30.0: set(v): spread = clampf(v, 0, 500)
@export var auto_free: bool = true

signal particles_emitted(count: int)


## Emite count partículas na posição global especificada.
## Se count <= 0, usa default_count.
## Retorna o array de nós instanciados (vazio se particle_scene for null).
func emit(at_position: Vector2 = Vector2.ZERO, color_override: Color = Color.WHITE, count: int = -1) -> Array[Node2D]:
	if count <= 0:
		count = default_count

	var spawned: Array[Node2D] = []

	for i in range(count):
		var particle: Node2D
		if particle_scene:
			particle = particle_scene.instantiate() as Node2D
		else:
			particle = _create_default_particle()

		if not particle:
			continue

		# Posição com dispersão aleatória
		var offset := Vector2(
			randf_range(-spread, spread),
			randf_range(-spread, spread)
		)
		particle.position = at_position + offset

		# Aplica cor
		_apply_color(particle, color_override)

		# Conecta auto-limpeza
		if auto_free:
			var gpup := particle as GPUParticles2D
			if gpup:
				gpup.finished.connect(_on_particle_finished.bind(particle), CONNECT_ONE_SHOT)
			else:
				var cpup := particle as CPUParticles2D
				if cpup:
					cpup.finished.connect(_on_particle_finished.bind(particle), CONNECT_ONE_SHOT)

		add_child(particle)

		# Dispara a emissão
		var gpup := particle as GPUParticles2D
		if gpup:
			gpup.one_shot = true
			gpup.emitting = true
		else:
			var cpup := particle as CPUParticles2D
			if cpup:
				cpup.one_shot = true
				cpup.emitting = true

		spawned.append(particle)

	particles_emitted.emit(spawned.size())
	return spawned


func _create_default_particle() -> GPUParticles2D:
	var gpup := GPUParticles2D.new()
	gpup.name = "DefaultParticle"
	gpup.amount = 8
	gpup.lifetime = 0.5
	gpup.one_shot = true
	gpup.explosiveness = 1.0

	var mat := ParticleProcessMaterial.new()
	mat.direction = Vector3(0, -1, 0)
	mat.spread = 180.0
	mat.initial_velocity_min = 80.0
	mat.initial_velocity_max = 160.0
	mat.gravity = Vector3(0, 200, 0)
	mat.scale_min = 4.0
	mat.scale_max = 8.0
	gpup.process_material = mat

	return gpup


func _apply_color(particle: Node2D, clr: Color) -> void:
	# Tenta aplicar no modulate do nó raiz da partícula
	particle.modulate = clr


func _on_particle_finished(p: Node2D) -> void:
	if is_instance_valid(p):
		p.queue_free()


func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray = []
		w.append("No specific configuration issues detected.")
	return w
