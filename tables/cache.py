import dill

def save_object(automaton, file_path):
    with open(file_path, 'wb') as file:
        dill.dump(automaton, file) 

def load_object(file_path):
    with open(file_path, 'rb') as file:
        loaded_object = dill.load(file)  
    return loaded_object