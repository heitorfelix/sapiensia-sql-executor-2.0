
import os
import pickle



# carregar os dados de login de um arquivo
def load_login_data():
    try:
        with open("./login/login_data.pkl", "rb") as f:
            login_data = pickle.load(f)
            return login_data["servers"], login_data["username"]
        
    except FileNotFoundError:
        return [""], ""
    
def save_login_data(server, username) -> None:

    file_path = "./login/login_data.pkl"

    if not os.path.exists(file_path): # se não existir nada acrescentar o primeiro server na lista
        servers = [server]

    else:
        servers, _ = load_login_data()

        if server not in servers:
            servers.append(server)
    
    with open(file_path, "wb") as f:
        login_data = {"servers" : servers , "username": username}
        pickle.dump(login_data, f)
    

def __init__():
    if not os.path.exists("./login"):
        os.mkdir('./login')