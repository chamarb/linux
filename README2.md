# How to ?

to build the docker image you'll have to :

```shell
$ docker build -t chama/web_home_page:0.0.1 -f Dockerfile .
$ docker images | head
```

Pour déployer une application Flask comme un service sous Linux :
## Activez le service et démarrez-le en utilisant les commandes suivantes :
```shell
$sudo nano /etc/systemd/system/flaskapp.service
$ sudo systemctl daemon-reload
$ sudo systemctl start myflaskapp
$ sudo systemctl enable myflaskapp
```
## Vérifiez que le service est en cours d'exécution en utilisant la commande :
```shell
$ sudo systemctl status myflaskapp
```
