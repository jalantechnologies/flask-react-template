SECRETS_DIR=/opt/app/secrets

for f in "$SECRETS_DIR"/*; do
  [ -f "$f" ] || continue
  name=$(basename "$f" | tr '[:lower:]' '[:upper:]')
  value=$(cat "$f")
  export "$name=$value"
done

exit 0