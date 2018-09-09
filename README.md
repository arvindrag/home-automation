README.md

Setup
clone repo
`pip install -r requirements.txt`

`sudo cp castbot.service /lib/systemd/system/castbot.service`

```
sudo systemctl daemon-reload
 sudo systemctl enable castbot.service
Reboot the Pi and your custom service should run :

sudo reboot
```