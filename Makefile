# Get the image name from the parent folder and set tag to 'dev'
IMAGE_NAME = screamcheck
TAG = dev

# Build the Docker image
HOST_UID := $(shell id -u)
HOST_GID := $(shell id -g)

build:
	docker build \
		--build-arg HOST_UID=$(HOST_UID) \
		--build-arg HOST_GID=$(HOST_GID) \
		-t $(IMAGE_NAME):$(TAG) .


run:
	docker run -it --rm \
		-v $(PWD):/app \
		-p 8080:8080 \
		$(IMAGE_NAME):$(TAG) bash

#directly run the server
serve:
	docker run -it --rm \
		-v $(PWD):/app \
		-p 5000:5000 \
		$(IMAGE_NAME):$(TAG) python3 ./src/app.py

clean:
	docker rmi $(IMAGE_NAME):$(TAG)

rebuild: clean build


