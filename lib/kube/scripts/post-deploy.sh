#!/bin/bash

kubectl rollout status deploy/"$KUBE_APP"-deployment -n "$KUBE_NS"

if [[ "$KUBE_ENV" != "preview" ]]; then
  kubectl rollout status deploy/"$KUBE_APP"-temporal-deployment -n "$KUBE_NS"
else
  echo "post-deploy :: skipping Temporal rollout check in preview environment"
fi