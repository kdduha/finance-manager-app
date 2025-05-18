#!/bin/bash

# create namespace
kubectl create namespace finance-app

# apply deployment + service
kubectl -n finance-app apply -f ./deploy/k8s/deployment.yaml

# install metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# patch metrics-server to skip TLS verification
kubectl patch deployment metrics-server -n kube-system \
  --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'

# wait for metrics-server pod to be ready
echo "Waiting for metrics-server to be ready..."
kubectl wait --for=condition=available --timeout=60s deployment/metrics-server -n kube-system

# add autoscaler
kubectl -n finance-app autoscale deployment finance-manager-app --cpu-percent=50 --min=2 --max=5

# wait a bit for pods to initialize
sleep 10

# port forwarding to the localhost
kubectl port-forward service/finance-manager-app-service 8000:8000 -n finance-app
