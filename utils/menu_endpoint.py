import re

def menu_endpoint(area, view):
    if not area or not view:
        return None

    area = area.strip().lower()
    view = view.strip().lower()

    # Map known views to actual view function names
    endpoint_map = {
        'user': {
            'userrole': 'manage_role',
            'manageuser': 'manage_user',
            'register': 'register',
        },
        # Add other blueprints/areas as needed
    }

    blueprint = f"{area}_blueprint"
    view_func = endpoint_map.get(area, {}).get(view)

    if view_func:
        return f"{blueprint}.{view_func}"

    return None  # fallback if not found
