# Minimální "Linux" pro pískoviště – malý, ale skutečný systém.
FROM alpine:3.20

# Základní nástroje, které se v úkolech používají (skutečné GNU/busybox binárky).
RUN apk add --no-cache \
        bash \
        coreutils \
        findutils \
        grep \
        sed \
        tree \
        file \
        ncurses \
        procps \
        iputils \
        tar \
        gzip

# Kontejner běží pod UID hostitele (--user), proto musí být /home zapisovatelné
# jen v bind-mountu; zbytek rootfs jede read-only.
ENV LANG=C.UTF-8 \
    TERM=xterm-256color \
    PS1='$ '

# Kontejner jen tiše čeká, příkazy do něj posílá `docker exec`.
CMD ["sleep", "infinity"]
