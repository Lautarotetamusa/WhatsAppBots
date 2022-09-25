# WhatsAppBots manager

Whatsapp bots manager. Send massive amout of messages without whatsapp bussiness api


## Installation

#### Clone the repository
```
  git clone https://github.com/Lautarotetamusa/WhatsAppBots.git
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

#### Start the server
```
  docker-compose up
```
