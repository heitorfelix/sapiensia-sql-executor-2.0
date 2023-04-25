# sapiensia-sql-executor-2.0

## Como instalar o executor no Windows
1. Instale o Python na máquina
2. Instale Ferramentas de compilação do Microsoft C++ - Visual Studio
Link para download do C++:   https://visualstudio.microsoft.com/pt-br/visual-cpp-build-tools/
3. Abra o terminal, faça o git clone deste repositório
4. Abra o diretório do projeto "./cd sapiensia-sql-executor"
5. Execute o comando "bash install.sh" para rodar o instalador
6. O instalador vai criar um ambiente virtual com todas dependências, e para executar o programa, basta executar o "execute.bat"

O executor cuida de ativar o ambiente virtual e abrir rodar o python script. Porém, pode ser interessate de abrir o app no terminal diretamente para caso dê erro o terminal não feche e possamos debugar.
