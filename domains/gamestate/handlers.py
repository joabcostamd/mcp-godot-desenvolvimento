"""domains/gamestate/handlers.py — F5.22."""
def create_save_system(*, scene_path: str, parent_node_path: str = ".") -> dict:
    from tools.devsolo_ops import create_save_system as _impl; return _impl(scene_path=scene_path, parent_node_path=parent_node_path)
def define_save_data(*, scene_path: str, data_name: str = "save_data", variables: list[str] | None = None) -> dict:
    from tools.devsolo_ops import define_save_data as _impl; return _impl(scene_path=scene_path, data_name=data_name, variables=variables)
def create_state_machine(*, scene_path: str, parent_node_path: str = ".", states: list[str] | None = None, initial_state: str = "") -> dict:
    from tools.devsolo_ops import create_state_machine as _impl; return _impl(scene_path=scene_path, parent_node_path=parent_node_path, states=states, initial_state=initial_state)
def add_state_transition(*, scene_path: str, fsm_path: str, from_state: str, to_state: str, condition: str = "") -> dict:
    from tools.devsolo_ops import add_state_transition as _impl; return _impl(scene_path=scene_path, fsm_path=fsm_path, from_state=from_state, to_state=to_state, condition=condition)
__all__ = ["create_save_system", "define_save_data", "create_state_machine", "add_state_transition"]
