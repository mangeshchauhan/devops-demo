# DevOps CI/CD Demo: Docker + Kubernetes + Argo CD

**Flow:** `git push` → GitHub Actions (test → build Docker image → push to GHCR → update manifest) → Argo CD detects the change → deploys to Kubernetes.

```
Developer ─push─▶ GitHub ─▶ GitHub Actions (CI)
                               │ test, build, push image
                               │ commit new image tag to k8s/
                               ▼
                           GitHub repo (single source of truth)
                               ▲
                               │ watches & syncs (CD)
                            Argo CD ─▶ Kubernetes cluster
```

## Prerequisites
Docker, kubectl, a local cluster (minikube or kind), a GitHub account, git.

## Step 1: Run the app locally
```bash
cd app && pip install -r requirements.txt && python app.py
# open http://localhost:5000
```

## Step 2: Containerize
```bash
docker build -t devops-demo:local .
docker run -p 5000:5000 devops-demo:local
```

## Step 3: Push the project to GitHub
Replace `YOUR_GITHUB_USERNAME` in `k8s/deployment.yaml` and `argocd/application.yaml` first. Create a public repo named `devops-demo`, then:
```bash
git init && git add . && git commit -m "initial"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/devops-demo.git
git push -u origin main
```

## Step 4: CI pipeline
The workflow in `.github/workflows/ci.yaml` runs on every push to `app/**` or the Dockerfile.
- Repo Settings → Actions → General → Workflow permissions → **Read and write**.
- After the first run: your profile → Packages → `devops-demo` → Settings → visibility **Public** (so the cluster can pull without a secret).

## Step 5: Create a Kubernetes cluster
```bash
minikube start        # or: kind create cluster
kubectl get nodes
```

## Step 6: Install Argo CD
```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl get pods -n argocd -w
```
Open the UI:
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# https://localhost:8080  user: admin
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

## Step 7: Register the app with Argo CD
```bash
kubectl apply -f argocd/application.yaml
```
Argo CD now watches the `k8s/` folder and syncs automatically.

## Step 8: Verify
```bash
kubectl get pods -n demo
kubectl port-forward svc/devops-demo -n demo 5001:80
# open http://localhost:5001
```

## Step 9: Live demo for students
1. Edit the heading in `app/app.py`.
2. `git pull` first (the bot pushes commits), then `git commit -am "change message" && git push`.
3. Watch GitHub Actions run, then the bot commit appear.
4. Watch Argo CD detect it and roll out new pods.
5. Refresh the browser: new version live, no manual `kubectl`.

**Rollback demo:** `git revert` the bot's commit and Argo CD restores the old version.
**Self-heal demo:** `kubectl delete deployment devops-demo -n demo` and Argo CD recreates it.

## Key concepts to teach
- **CI vs CD:** GitHub Actions builds artifacts; Argo CD delivers them.
- **GitOps:** Git is the single source of truth; the cluster pulls its state from it.
- **Immutable tags:** Images are tagged with the commit SHA (traceable, easy rollback).
- **Self-healing and drift detection** with Argo CD.

## Ideas to extend
Ingress, Helm or Kustomize, separate config repo, staging/prod environments, image scanning (Trivy), Slack notifications.
