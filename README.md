# Simple chat test task


---
## Table of Contents

1. [Getting started](#getting-started)
2. [Authentication](#authentication)
3. [Thread Endpoints](#thread-endpoints)
4. [Message Endpoints](#message-endpoints)
---

## Getting Started

Follow the next guide to set up the application

### 1. **Prerequisites**

Before you begin, ensure you have the following installed on your system:

- **Docker**
- **CLI:** You can just run `sh entrypoint.sh`

*Generally speaking, Docker is more preferable in this case*

### 2. **Clone the Repository**

Start by cloning your project repository to your local machine.

```bash
git clone https://github.com/ronylitv14/Simple-chat.git
cd Simple-chat
```

### 3. **Prepare the Environment**

Ensure that the `db_test_data.json` file is present in the root directory of project. This file contains the necessary test data that will be loaded into the Docker container during setup.
Ensure you have added `.env` file to root of cloned directory like is stated in `.env-example`

```
SECRET_KEY=some-secret-django-key
JWT_LIFETIME=10
```

### 4. **Build the Docker Image**

Use the provided `Dockerfile` to build the Docker image for your application.

```bash
docker build -t django-simple-chat:v1 .
```

### 5. **Run the Docker Container**

Start the Docker container using the built image. This will set up the application along with the test data.

```bash
docker run -p 8000:8000 --name simple-chat django-simple-chat:v1
```

**Notes:**
- **Port Mapping:** Ensure that port `8000` is available on your host machine. If it's occupied, you can change the host port by modifying the `-p` flag (e.g., `-p 8080:8000`).
- **Detached Mode (`-d`):** Runs the container in the background (if it's needed)

### 6. **Accessing the Application**

Once the container is running, you can access the application API at:

```
http://0.0.0.0:8000/api/
```

### 7. **Authenticate and Obtain Tokens**

To interact with the API endpoints, you need to authenticate and obtain access and refresh tokens.

**Test Users:**

- **Superuser:**
  - **Username:** `test-superuser`
  - **Password:** `Password123`
  
- **Regular User:**
  - **Username:** `test-user`
  - **Password:** `NewPassword123`

**Authentication Endpoint:**
```
POST /api/token/
```

**Request Body:**
```json
{
    "username": "test-user",
    "password": "NewPassword123"
}
```

**Example Request Using cURL:**
```bash
curl -X POST http://localhost:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "test-user", "password": "NewPassword123"}'
```

**Example Response:**
```json
{
    "access": "your_access_token_here",
    "refresh": "your_refresh_token_here"
}
```

### 8. **Using the Access Token for API Requests**

Include the obtained access token in the `Authorization` header of your API requests to authenticate.

**Authorization Header Format:**
```
Authorization: Bearer your_access_token_here
```

**Example cURL Request:**
```bash
curl -X GET http://localhost:8000/api/threads/ \
     -H "Authorization: Bearer your_access_token_here"
```

## Authentication

All API endpoints require authentication. Use token-based authentication by including the token in the `Authorization` header of your requests.

**Example Header:**
```
Authorization: Bearer your_token_here
```

---

## Thread Endpoints

### 1. Create or Retrieve Thread

**Endpoint:**
```
POST /api/threads/
```

**Description:**
Creates a new thread with specified participants. If a thread with the exact set of participants already exists, it returns the existing thread instead of creating a new one. A thread must have exactly **2 unique participants**, including the authenticated user.

**Request Body:**
```json
{
    "participants": [2]
}
```

**Validation Rules:**
- **At Least One Participant:** The `participants` field must include at least one user ID.
- **Exactly Two Unique Participants:** Including the authenticated user, a thread must have exactly two unique participants.

**Responses:**

- **200 OK** (Thread exists)
    ```json
    {
        "id": 10,
        "participants": [1, 2],
        "created": "2024-04-01T12:34:56Z",
        "updated": "2024-04-02T14:20:30Z"
    }
    ```
  
- **201 Created** (Thread created)
    ```json
    {
        "id": 11,
        "participants": [1, 3],
        "created": "2024-04-03T10:00:00Z",
        "updated": "2024-04-03T10:00:00Z"
    }
    ```

- **400 Bad Request** (Validation Errors)
    ```json
    {
        "participants": [
            "There should be at least 1 participant.",
            "A thread must have exactly 2 unique participants."
        ]
    }
    ```

**Example Request:**
```
POST /api/threads/
Content-Type: application/json

{
    "participants": [2]
}
```

**Example Response:**
```json
{
    "id": 10,
    "participants": [1, 2],
    "created": "2024-04-01T12:34:56Z",
    "updated": "2024-04-01T12:34:56Z"
}
```

### 2. Remove Thread

**Endpoint:**
```
DELETE /api/threads/{id}/
```

**Description:**
Deletes a specific thread. Only **staff members** or **participants of the thread** can perform this action.

**Parameters:**
- `id` (path): ID of the thread to delete.

**Responses:**

- **204 No Content**

- **403 Forbidden**
    ```json
    {
        "detail": "You do not have permission to delete this thread."
    }
    ```

- **404 Not Found**
    ```json
    {
        "detail": "Not found."
    }
    ```

**Example Request:**
```
DELETE /api/threads/10/
```

### 3. List Threads

**Endpoint:**
```
GET /api/threads/
```

**Description:**
Retrieves a list of threads that the authenticated user is a participant in. **Staff users** can filter threads by a specific user ID using the `user_id` query parameter.

**Query Parameters:**
- `user_id` (optional): Filter threads to include a specific user.

**Responses:**

- **200 OK**
    ```json
    [
        {
            "id": 10,
            "participants": [1, 2],
            "created": "2024-04-01T12:34:56Z",
            "updated": "2024-04-02T14:20:30Z"
        },
        {
            "id": 12,
            "participants": [1, 3],
            "created": "2024-04-05T09:15:00Z",
            "updated": "2024-04-05T09:15:00Z"
        }
    ]
    ```

- **401 Unauthorized**
    ```json
    {
        "detail": "Authentication credentials were not provided."
    }
    ```

**Example Request:**
```
GET /api/threads/?user_id=2
```

---

## Message Endpoints

### 1. Create Message

**Endpoint:**
```
POST /api/messages/
```

**Description:**
Sends a new message within a specified thread. The authenticated user is automatically set as the sender. Upon creation, the thread's `updated` timestamp is refreshed.

**Request Body:**
```json
{
    "thread": 10,
    "text": "Hello, how are you?"
}
```

**Responses:**

- **201 Created**
    ```json
    {
        "id": 15,
        "sender": 1,
        "text": "Hello, how are you?",
        "thread": 10,
        "created": "2024-04-01T13:00:00Z",
        "is_read": false
    }
    ```

- **400 Bad Request**
    ```json
    {
        "thread": ["This field is required."],
        "text": ["This field cannot be blank."]
    }
    ```

- **403 Forbidden**
    ```json
    {
        "detail": "You do not have permission to send messages to this thread."
    }
    ```

**Example Request:**
```
POST /api/messages/
Content-Type: application/json

{
    "thread": 10,
    "text": "Hello, how are you?"
}
```

### 2. List Messages

**Endpoint:**
```
GET /api/messages/?thread_id={thread_id}&limit={limit}&offset={offset}
```

**Description:**
Retrieves a paginated list of messages within a specific thread. Only accessible to participants of the thread.

**Query Parameters:**
- `thread_id` (required): ID of the thread.
- `limit` (optional): Number of messages per page.
- `offset` (optional): Starting index for messages.

**Responses:**

- **200 OK**
    ```json
    {
        "count": 50,
        "next": "/api/messages/?thread_id=10&limit=10&offset=10",
        "previous": null,
        "results": [
            {
                "id": 15,
                "sender": 1,
                "text": "Hello, how are you?",
                "thread": 10,
                "created": "2024-04-01T13:00:00Z",
                "is_read": false
            }
        ]
    }
    ```

- **400 Bad Request**
    ```json
    {
        "thread_id": ["This query parameter is required."]
    }
    ```

- **401 Unauthorized**
    ```json
    {
        "detail": "Authentication credentials were not provided."
    }
    ```

**Example Request:**
```
GET /api/messages/?thread_id=10&limit=20&offset=0
```

### 3. Mark Message as Read

**Endpoint:**
```
POST /api/messages/{id}/mark_as_read/
```

**Description:**
Marks a specific message as read. Only the intended recipient can perform this action.

**Parameters:**
- `id` (path): ID of the message to mark as read.

**Request Body:**
```json
{
    "is_read": true
}
```

**Responses:**

- **200 OK**
    ```json
    {
        "status": "message marked as read"
    }
    ```

- **400 Bad Request**
    ```json
    {
        "is_read": ["This field is required."]
    }
    ```

- **403 Forbidden**
    ```json
    {
        "detail": "You do not have permission to mark this message as read."
    }
    ```

- **404 Not Found**
    ```json
    {
        "detail": "Not found."
    }
    ```

**Example Request:**
```
POST /api/messages/15/mark_as_read/
Content-Type: application/json

{
    "is_read": true
}
```

### 4. Unread Messages Count

**Endpoint:**
```
GET /api/messages/unread/
```

**Description:**
Retrieves the count of unread messages for the authenticated user across all threads.

**Responses:**

- **200 OK**
    ```json
    {
        "unread_count": 5
    }
    ```

- **401 Unauthorized**
    ```json
    {
        "detail": "Authentication credentials were not provided."
    }
    ```

**Example Request:**
```
GET /api/messages/unread/
```

---
