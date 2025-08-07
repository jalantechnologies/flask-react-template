#!/bin/bash

kubectl rollout status deploy/"$KUBE_APP"-deployment -n "$KUBE_NS"
kubectl rollout status deploy/"$KUBE_APP"-temporal-deployment -n "$KUBE_NS"
