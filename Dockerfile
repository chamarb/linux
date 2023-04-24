FROM --platform=amd64 ubuntu:latest

LABEL author="Chama Rouineb<rouineb.online@gmail.com>"

RUN apt update -y && apt install -y python3

COPY src /src

ENTRYPOINT [ "/usr/bin/python3" ]
CMD [ "/src/app.py" ]