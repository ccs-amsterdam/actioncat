FROM r-base

# install system dependencies
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
    curl \
    libssl-dev \
    libcurl4-openssl-dev \
    libxml2-dev

# copy script
COPY . /usr/local/src/myscripts
WORKDIR /usr/local/src/myscripts
RUN ["Rscript", "dependencies.r"]

# install dependencies and run script
CMD ["Rscript", "dfm.r"]
