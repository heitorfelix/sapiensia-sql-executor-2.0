
import os
import pickle

# salvar os dados de login em um arquivo
def save_login_data(server, username):

    if not os.path.exists("./login"):
        os.mkdir('./login')

    with open("./login/login_data.pkl", "wb") as f:
        login_data = {"server": server, "username": username}
        pickle.dump(login_data, f)

# carregar os dados de login de um arquivo
def load_login_data():
    try:
        with open("./login/login_data.pkl", "rb") as f:
            login_data = pickle.load(f)
            return login_data["server"], login_data["username"]
    except FileNotFoundError:
        return "", "", ""
    

