# create a namespace for monitoring (Grafana, Prometheus)
kubectl create namespace monitoring

# add the Prometheus community Helm chart repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# install Prometheus and Grafana using the kube-prometheus-stack Helm chart in the monitoring namespace
helm install prometheus \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring

# retrieve the admin password for Grafana
kubectl --namespace monitoring get secrets prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 -d ; echo

# apply the ServiceMonitor configuration to the monitoring namespace to enable Prometheus scraping of metrics
kubectl -n monitoring apply -f ./deploy/k8s/service_monitor.yaml

# port forwarding to the localhost
kubectl wait --for=condition=available --timeout=180s deployment/prometheus-grafana -n monitoring
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
