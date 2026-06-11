import uuid

from locust import HttpUser, task, between


class TaskAPIUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        suffix = uuid.uuid4().hex[:8]
        username = f"user_{suffix}"
        email = f"user_{suffix}@example.com"
        password = "SecurePassword123!"

        with self.client.post("/users/register", json={
            "username": username,
            "email": email,
            "password": password
        }, catch_response=True) as reg_response:
            if reg_response.status_code not in [200, 201]:
                reg_response.failure(f"Registration failed: {reg_response.text}")
                self.stop()
                return

        with self.client.post("/users/login", json={
            "email": email,
            "password": password
        }, catch_response=True) as login_response:
            if login_response.status_code != 200:
                login_response.failure(f"Login failed: {login_response.text}")
                self.stop()
                return

            token = login_response.json().get("access_token")
            if not token:
                login_response.failure("Token missing")
                self.stop()
                return

        self.client.headers["Authorization"] = f"Bearer {token}"

    @task(4)
    def view_tasks_list(self):
        self.client.get("/tasks")

    @task(2)
    def task_lifecycle_workflow(self):
        create_resp = self.client.post("/tasks", json={
            "title": "Locust Test Task",
            "description": "Synthetic task description",
            "priority": 3
        })
        if create_resp.status_code == 201:
            task_id = create_resp.json().get("id")
            self.client.get(f"/tasks/{task_id}")
            self.client.put(f"/tasks/{task_id}/complete")
            self.client.delete(f"/tasks/{task_id}")

    @task(1)
    def query_system_diagnostics(self):
        self.client.get("/system/ping")
        self.client.get("/system/info")
        self.client.get("/system/health")
