#!/bin/bash
kubectl get secret argocd-initial-admin-secret -n argocd -o yaml | grep password: | awk '{print $2}' | base64 --decode ; echo \r
