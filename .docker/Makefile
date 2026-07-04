GIT_TAG ?= master
TAG ?= latest
NAMESPACE ?= tloj

.PHONY: all judge-tier1 judge-tier2 judge-tier3 judge-tiervnoj judge-tiericpc

all: judge-tier1 judge-tier2 judge-tier3 judge-tiervnoj judge-tiericpc

judge-tier1:
	docker build --build-arg TAG="${GIT_TAG}" -t $(NAMESPACE)/judge-tier1 -t $(NAMESPACE)/judge-tier1:$(TAG) tier1

judge-tier2:
	docker build --build-arg TAG="${GIT_TAG}" -t $(NAMESPACE)/judge-tier2 -t $(NAMESPACE)/judge-tier2:$(TAG) tier2

judge-tier3:
	docker build --build-arg TAG="${GIT_TAG}" -t $(NAMESPACE)/judge-tier3 -t $(NAMESPACE)/judge-tier3:$(TAG) tier3

judge-tiervnoj:
	docker build --build-arg TAG="${GIT_TAG}" -t $(NAMESPACE)/judge-tiervnoj -t $(NAMESPACE)/judge-tiervnoj:$(TAG) tiervnoj

judge-tiericpc:
	docker build --build-arg TAG="${GIT_TAG}" -t $(NAMESPACE)/judge-tiericpc -t $(NAMESPACE)/judge-tiericpc:$(TAG) tiericpc
