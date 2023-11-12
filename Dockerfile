# FROM selenium/standalone-firefox:latest
FROM ubuntu:jammy


# Set timezone
RUN apt-get update && \
    apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

RUN apt-get update && \
    apt-get install -y apt-transport-https wget gpg python3-pip lsb-release glibc-source libgtk-3-0 libdbus-glib-1-dev libglib2.0-0 libstdc++6 libxtst6 xorg openbox libdbus-1-dev network-manager pulseaudio

ARG ARCHITECTURE="dpkg --print-architecture" \
    RELEASEARCH='if [ "$(eval ${ARCHITECTURE})"=="amd64" ]; then echo "linux64"; else echo "linux32"; fi' \
    LATESTVERSION='curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep tag_name | cut -d \" -f 4' \
    DISTRIBUTION="lsb_release -cs"

# install Tor
RUN echo \
"deb [signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org $(eval ${DISTRIBUTION}) main\n\
deb-src [signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org $(eval ${DISTRIBUTION}) main\n\
deb     [arch=$(eval ${ARCHITECTURE}) signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org focal main\n\
deb-src [arch=$(eval ${ARCHITECTURE}) signed-by=/usr/share/keyrings/tor-archive-keyring.gpg] https://deb.torproject.org/torproject.org focal main" > /etc/apt/sources.list.d/tor.list &&\
    wget -qO- https://deb.torproject.org/torproject.org/A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89.asc | gpg --dearmor | tee /usr/share/keyrings/tor-archive-keyring.gpg >/dev/null && \
    apt-get update && \
    apt-get install -y tor deb.torproject.org-keyring curl git

#install geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-$(eval ${LATESTVERSION})-$(eval ${RELEASEARCH}).tar.gz && \
    tar xvf geckodriver-$(eval ${LATESTVERSION})-$(eval ${RELEASEARCH}).tar.gz && \
    mv geckodriver /usr/bin/ &&\
    rm geckodriver-$(eval ${LATESTVERSION})-$(eval ${RELEASEARCH}).tar.gz

#install firefox
RUN wget https://download-installer.cdn.mozilla.net/pub/firefox/releases/119.0.1/linux-x86_64/ko/firefox-119.0.1.tar.bz2 &&\
    tar xjf firefox-119.0.1.tar.bz2 &&\
    mv firefox /opt &&\
    ln -s /opt/firefox/firefox /usr/local/bin/firefox &&\
    rm firefox-119.0.1.tar.bz2

#install crawler & dependencies
RUN git clone https://github.com/yeardream-final-project-06team/youtube-crawler.git &&\
    cd /youtube-crawler &&\
    pip3 install -r requirements.txt &&\
    pip3 install -e ./

RUN echo "service tor start" >> /root/.bashrc
