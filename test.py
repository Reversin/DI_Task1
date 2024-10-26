import requests

url = "http://localhost:8000/users/"

users = [
    {"email": f"user{i}@example.com", "full_name": f"User {i}"}
    for i in range(1, 10)
]

for user in users:
    response = requests.post(url, json=user)
    if response.status_code == 200:
        print(f"User created: {user['email']}")
    else:
        print(f"Failed to create user {user['email']}: {response.json().get('detail', 'No detail available')}")
