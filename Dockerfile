FROM fedora:25

RUN dnf install --setopt=tsflags=nodocs -y \
    python2-aexpect \
    python2-avocado \
    python2-modulemd \
    python-enchant \
    hunspell-en-US \
    python2-dnf && \
    dnf clean all

COPY . /app

WORKDIR "/"

# users are epxected to mount the modulemd at /
# otherwise they can run bash inside the container and run the test themselves
CMD /app/run-checkmmd.sh /*.yaml ; cat /root/avocado/job-results/latest/job.log
