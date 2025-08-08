from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="localhost")

print("=== ROUTES LOADED ===")
for rule in app.url_map.iter_rules():
    print(rule)
print("=====================")
