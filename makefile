#déployer l'application Flask comme un service sous Linux, vous pouvez utiliser Systemd. 
#Créez un fichier de service nommé app.service dans le répertoire /etc/systemd/system
[Unit]
Description=My Flask Application
After=network.target

[Service]
User=myuser
Group=mygroup
WorkingDirectory=/path/to/app
ExecStart=/usr/bin/python /path/to/app/app.py
Restart=always

[Install]
WantedBy=multi-user.target
