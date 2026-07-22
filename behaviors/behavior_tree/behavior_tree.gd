## Node que executa uma árvore de comportamento (BT) simplificada com tick_rate configurável.
## Generos: generic.
## Tags: bt, behavior_tree, ia.
## Extends: Node.
## Sinais: tree_started(), tree_stopped(), node_executed().
## Dependencias: blackboard.
## @behavior: behavior_tree
@tool class_name BehaviorTree extends Node
@export var tick_rate: float = 0.1: set(v)=tick_rate=clampf(v,0.01,60.0)
@export var tree_data: Array = []
signal tree_started()
signal tree_stopped()
signal node_executed(node_name: String, status: String)
var _running: bool = false
var _tick_timer: float = 0.0
var _blackboard: Blackboard = null
var _initialized: bool = false
func _ready() -> void:
	if _initialized: return
	_find_blackboard(); _initialized=true
func _find_blackboard() -> void:
	var p:=get_parent(); if not p: return
	for c in p.get_children():
		if c is Blackboard: _blackboard=c as Blackboard; return
func _process(delta: float) -> void:
	if not _running: return
	_tick_timer+=delta
	if _tick_timer>=tick_rate: _tick_timer=0.0; _tick()
func start() -> void:
	if _running: return; _running=true; tree_started.emit()
func stop() -> void:
	if not _running: return; _running=false; tree_stopped.emit()
func _tick() -> void:
	_execute_node(tree_data)
func _execute_node(node: Dictionary) -> String:
	var type:=node.get("type","") as String; var name:=node.get("name","") as String
	match type:
		"sequence":
			var seq_children: Array=node.get("children",[])
			for child in seq_children:
				var stat:=_execute_node(child as Dictionary)
				if stat=="failure": node_executed.emit(name,"failure"); return "failure"
			node_executed.emit(name,"success"); return "success"
		"selector":
			var sel_children: Array=node.get("children",[])
			for child in sel_children:
				var sel_stat:=_execute_node(child as Dictionary)
				if sel_stat=="success": node_executed.emit(name,"success"); return "success"
			node_executed.emit(name,"failure"); return "failure"
		"action":
			var method:=node.get("action_method","") as String
			var act_status:="success"
			if not method.is_empty() and has_method(method): act_status="success" if call(method) else "failure"
			else: act_status="success"
			node_executed.emit(name,act_status); return act_status
	return "success"
func is_running() -> bool: return _running
func _get_configuration_warnings() -> PackedStringArray:
	var w: PackedStringArray=[]
	if tree_data.is_empty(): w.append("tree_data vazio.")
	return w
