#!/bin/bash

kubectl rollout status deploy/"$KUBE_APP"-deployment -n "$KUBE_NS"

# TODO: https://github.com/jalantechnologies/flask-react-template/issues/274
# Temporary workaround to avoid Temporal rollout check failure in preview env
if [[ "$KUBE_ENV" != "preview" ]]; then
  kubectl rollout status deploy/"$KUBE_APP"-temporal-deployment -n "$KUBE_NS"
else
  echo "post-deploy :: skipping Temporal rollout check in preview environment"
fi
