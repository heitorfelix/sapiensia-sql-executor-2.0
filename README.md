# MultiQuery Executor

## Como instalar o executor no Windows
1. Instale o Python na máquina
2. Instale Ferramentas de compilação do Microsoft C++ - Visual Studio e reinicie a máquina
Link para download do C++:   https://visualstudio.microsoft.com/pt-br/visual-cpp-build-tools/
3. Abra o terminal, faça o git clone deste repositório
4. Abra o diretório do projeto "./cd sapiensia-sql-executor"
5. Execute o comando "bash install.sh" para rodar o instalador
6. O instalador vai instalar todas dependências, e para executar o programa, basta executar o "run_app.bat"

### Tela de Login

![Alt text](image.png)

Aqui você deve colocar as credenciais e servidor a ser conectado. 

Caso você não tenha nenhum servidor cadastrado, clique neste botão para escrever o servidor. 

![Alt text](image-1.png)

![Alt text](image-2.png)

Ao conseguir executar, o servidor ficará salvo numa ComboBox 

![Alt text](image-3.png)

Para executar query do tipo SELECT, que retorne resultados selecione "Query (SQL)" e caso contrário utilize "DDL/DML" para executar INSERT, ALTER, DROP, DELETE, GRANT ou qualquer comando que não retorne resultados.
Mais detalhes será mostrado a seguir de cada tela

### DQL Window

Para utilizar essa tela é bem simples, basta selecionar os bancos que você quer executar o script e clicar no botão. 

![Alt text](image-4.png)

Caso não exista o objeto no Banco ou dê algum erro, ele será exibido numa MessageBox:

![Alt text](image-5.png)

Depois de todos erros exibidos na tela, naqueles que tenha tido sucesso os resultados aparecerão no grid junto com o DatabaseName:

![Alt text](image-6.png)

Você pode alternar para página de **DDL/DQL** no menu **Pages**

![Alt text](image-7.png)

### DML/DQL

Para utilizar essa tela é exatamente igual a tela de DQL, basta selecionar os bancos que você quer executar o script e clicar no botão. 

![Alt text](image-8.png)

Caso não exista o objeto no Banco ou dê algum erro, ele será exibido no grid. E caso a execução funcione ele aparecerá "Executado em sucesso". Os erros aparecem primeiro.

![Alt text](image-9.png)

### Salvar resultados

Em ambas telas é possível exportar os resultados em Excel ou CSV. 

![Alt text](image-10.png)

Os caminho para onde os dados vão é por padrão na pasta "dados" no diretório da aplicação:

![Alt text](image-11.png)

![Alt text](image-12.png)

![Alt text](image-13.png)

### Configurações avançadas

Para utilizar configurações que podem te ajudar a melhorar a experiência com a ferramenta, você deve ir em **Options** no menu e em **Configration**

![Alt text](image-14.png)

Ela abrirá uma tela onde você pode selecionar alguns parâmetros

![Alt text](image-15.png)

Você pode selecionar bancos de dados que você não quer que apareçam na listagem, e uma opção para que sempre filtre esses bancos na blacklist. 
Além disso você pode personalizar o caminho para onde os dados exportados vão. 
Para salvar as configurações, basta clicar em **Save Config** e para limpar as configurações salvas basta clicar em **Clear Config**. 

As configurações são persistidas por servidor, então você precisa configurar esses parâmetros para cada servidor.

#### Blacklist

Esta é a lista de todos bancos de dados que você não quer ver, por exemplo, como pode-se observar na última imagem. Eu só quero que exiba os bancos Drake, então os demais estão selecionados na blacklist.

No menu você pode ligar e desligar o filtro a vontade.

![Alt text](image-14.png)
