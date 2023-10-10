def history_to_role_content(history):
    role_content_list = []
    for visible_interaction in history['visible']:
        user_content, assistant_content = visible_interaction
        role_content_list.append({'role': 'user', 'content': user_content})
        if assistant_content:  # Only add the assistant's reply if it's not empty
            role_content_list.append({'role': 'assistant', 'content': assistant_content})
    return role_content_list

def role_content_to_history(role_content_list):
    history = {
        'internal': [],
        'visible': []
    }
    
    for i in range(0, len(role_content_list), 2):  # Iterate by twos to get user and (possible) assistant pairs
        user_content = role_content_list[i]['content']
        assistant_content = role_content_list[i+1]['content'] if (i+1 < len(role_content_list) and role_content_list[i+1]['role'] == 'assistant') else ''
        
        history['internal'].append([user_content, assistant_content])
        history['visible'].append([user_content, assistant_content])
    
    return history