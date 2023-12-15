# Visão geral
Este é um projeto em desenvolvimento de um aplicativo Android simples, criado em Python com o uso do framework Kivy/KivyMD. O aplicativo permite a pesquisa e download de vídeos/músicas do YouTube, oferecendo uma funcionalidade principal bem desenvolvida. Por favor, esteja ciente de que o aplicativo ainda está em fase de desenvolvimento e pode conter erros. O código fonte não está documentado neste momento.

# Compatibilidade Testada:
+ Android (10, 14)
+ Windows (10, 11)
+ Linux

# Requisitos de Execução:
+ Python3
+ KivyMD (https://github.com/KivyMD/KivyMD/archive/master.zip)
+ Kivy (versão 2.2.0.dev0)
+ Youtube-Search-Python
+ PyTube
+ Httpx
+ Mutagen
+ Plyer
+ Certifi
+ watchdog

# Aviso
Seu funcionamento depende da bibliotéca PyTube e da API do YouTube. Qualquer alteração nos requisitos mencionados pode resultar em erros no aplicativo, estamos trabalhando para melhorá-lo e corrigir quaisquer problemas.

# Uso
+ Ao abrir o aplicativo, você verá uma entrada de texto que aceita o nome de vídeos ou playlists (não implementado ainda) do YouTube, bem como os links correspondentes.
+ Pasta de saída: /Downloads/YTDL

# Execução
+ Considerando que você ja tenha instalado o Python3, é recomendado criar um ambiente virtual para instalar os pacotes necessários para a execução do programa para não interferir com as versões já instaladas no seu sistema.

### Windows
+ Na pasta raiz do projeto, crie um ambiente virtual
```
python3 -m venv env
```
+ Abilite a execução de scripts PowerShell
```
Set-ExecutionPolicy Unrestricted -Scope Process
```
+ Ative o ambiente virtual (deve aparecer (env) antes do diretorio atual)
```
.\env\Scripts\Activate.ps1
```
+ Instale as dependencias necessárias
```
pip3 install -r requirements.txt
```
+ Execute o projeto
```
.\env\Scripts\python3.exe .\src\main.py
```

### Linux
+ Na pasta raiz do projeto, crie um ambiente virtual
```
python3 -m venv env
```
+ Ative o ambiente virtual (deve aparecer (env) antes do diretorio atual)
```
source ./env/bin/activate
```
+ Instale as dependencias necessárias
```
pip3 install -r requirements.txt
```
+ Execute o projeto
```
./env/bin/python3 ./src/main.py
```

# Binário
+ Para gerar um binário e compilar para uma plataforma específica será necessário o uso de algumas bibliotécas: [PyInstaller](https://pyinstaller.org/en/stable/) para Windows/Linux e [Buildozer](https://buildozer.readthedocs.io/en/latest/) para Android.

### Windows/Linux
+ Instale a bibliotéca PyInstaller
```
pip3 install pyinstaller
```
+ Navegue até a pasta **build** e execute o seguinte comando
```
*Linux*
pyinstaller --name app-linux --onefile --add-data "data:data" --add-data "mainapp.kv:." --hidden-import httpx --hidden-import youtubesearchpython --hidden-import mutagen --hidden-import plyer main.py

*Windows*
pyinstaller --name app-win --onefile --add-data "data;data" --add-data "mainapp.kv;." --hidden-import httpx --hidden-import youtubesearchpython --hidden-import mutagen --hidden-import plyer main.py
```
