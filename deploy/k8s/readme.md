## How to run the app in k8s?

- Run minikube with cmd:
```sh
minikube start
```

- Deploy the app with `Makefile` cmd from the repo root:
```sh
make build-k8s
```

- Check `localhost:8000` address 

- In order to deploy grafana and prometheus run:
```sh
make monitor-k8s
```