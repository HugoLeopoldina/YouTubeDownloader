# Tópicos
+ [Visão geral](#visão-geral)
+ [Compatibilidades](#compatibilidade-testada)
+ [Avisos](#aviso)
+ [Uso](#uso)
+ [Execução](#execução)
+ [Compilação](#compilação)
+ [Downloads](#download-mediafire)

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
Seu funcionamento depende da bibliotéca PyTube e da API do YouTube. Qualquer alteração nos requisitos mencionados pode resultar em erros no aplicativo, estamos trabalhando para melhorá-lo e corrigir quaisquer problemas. No Android recomendamos que permita o acesso ao armazenamento manualmente (acessando as informações do aplicativo nas configurações) caso necessário ou caso de erros ao efetuar algum download.

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
.\env\Scripts\python.exe .\src\main.py
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

# Compilação
+ Para gerar um binário e compilar para uma plataforma específica será necessário o uso de algumas bibliotécas: [PyInstaller](https://pyinstaller.org/en/stable/) para Windows/Linux e [Buildozer](https://buildozer.readthedocs.io/en/latest/) para Android.

### Windows/Linux
+ Instale a bibliotéca PyInstaller
```
pip3 install pyinstaller
```
+ Navegue até a pasta **build** e execute o seguinte comando no Windows
```
pyinstaller --name app-win --onefile --add-data "data;data" --add-data "mainapp.kv;." --hidden-import httpx --hidden-import youtubesearchpython --hidden-import mutagen --hidden-import plyer main.py
```
+ Ou no Linux
```
pyinstaller --name app-linux --onefile --add-data "data:data" --add-data "mainapp.kv:." --hidden-import httpx --hidden-import youtubesearchpython --hidden-import mutagen --hidden-import plyer main.py
```
+ Irá gerar uma pasta **build** e **dist**, basta executar o binário na pasta **dist** no windows
```
.\dist\app-win.exe
```
+ Ou no Linux
```
./dist/app-linux
```

### Android
+ Para construir um apk apartir do python será necessário o sistema operacional Linux pois o [Buildozer](https://buildozer.readthedocs.io/en/latest/) é dependente de algumas bibliotécas ou ferramentas especificas para sistema Linux. Para superar essa incompatibilidade do Windows será necessário o uso do [Subsystem for Linux (WSL)](https://learn.microsoft.com/pt-br/windows/wsl/install).
+ Considerando que já esteja com um terminal linux em execução, siga as instruções de instalação do **buildozer** [aqui](https://buildozer.readthedocs.io/en/latest/installation.html), navegue até a pasta **src** e execute o comando
```
buildozer android debug
```
+ O processo pode demonerar de 15 à 30 minutos, ao terminar o apk gerado estará na pasta **bin**

# Downloads (mediafire)
+ [Android](https://www.mediafire.com/file/llhokxh68j2wpbn/YouTubeDL.apk/file)
+ [Windows](https://www.mediafire.com/file/dpnmtjm7rgzg5b0/YouTubeDL.exe/file)
+ [Linux](https://www.mediafire.com/file/x1j23pdjqh2g50s/YouTubeDL/file)
