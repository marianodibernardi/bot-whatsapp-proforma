user_states = {}
user_selected_proforma = {}

def get_state(user_id):
    return user_states.get(user_id, "inicio")

def set_state(user_id, state, selected_proforma=None):
    user_states[user_id] = state
    if selected_proforma:
        user_selected_proforma[user_id] = selected_proforma

def get_selected_proforma(user_id):
    return user_selected_proforma.get(user_id)
