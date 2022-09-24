# WhatsAppBots manager

Whatsapp bots manager. Send massive amout of messages without whatsapp bussiness api


## Installation

#### Clone the repository
```
  git clone https://github.com/Lautarotetamusa/WhatsAppBots.git
```

#### Install python 3.10.6
```
  sudo apt install python
  sudo apt install python-pip
  sudo apt install python-venv
```

#### Install chromium==105.0.5195.52 and chromedriver==105.0.5195.52
```
  sudo snap install chromium
  sudo apt install chromium-chromedriver
```
#### Install and run virtual display
```
  sudo apt install xvfb
  Xvfb :10 -ac -screen 0 1024x768x8 &
  export DISPLAY=:10
```

#### Make virtual enviroment
```
  python -m venv .venv
  source .venv/bin/activate
```

#### Install requirements
```
  pip install -r requirements.txt
```

### Migrate the DataBases
```
  python manage.py migrate
```

#### Run the server
```
  python manage.py runserver
