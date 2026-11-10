# FastAPI Blog

A blog application with a server-rendered web interface and a JSON API. Built with FastAPI, async SQLAlchemy, SQLite, Jinja2, and Bootstrap.

## Features

- Browse posts from newest to oldest, open individual posts, and view posts by author.
- Create, edit, and delete posts through the API or browser modals.
- Register an account and log in with an email address and password.
- Hash passwords with Argon2 and issue JWT access tokens.
- Retrieve the signed-in user's profile through a protected endpoint.
- Switch between light, dark, and system themes.
- Return JSON errors for API requests and HTML error pages for browser requests.

Authentication is partly integrated. See [Current limitations](#current-limitations) for the access rules and browser behavior.

## Getting started

### Requirements

- Python 3.13 or newer; `.python-version` selects Python 3.13.
- `uv` for dependency management.

Run all commands from the project root so the app can find its templates, static files, media, and `.env` file.

### 1. Install dependencies

```bash
uv sync --locked
```

This creates a local `.venv` and installs the dependencies from `uv.lock`.

### 2. Configure the application

Generate a signing key:

```bash
uv run python -c "import secrets; print(secrets.token_hex(32))"
```

Create a `.env` file in the project root and paste the generated key into `SECRET_KEY`:

```dotenv
SECRET_KEY=replace-with-your-generated-key
```

The app reads settings from environment variables or `.env`. Environment variables take precedence.

| Variable | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | Required | Signs and verifies JWT access tokens. |
| `ALGORITHM` | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime in minutes. |

The app will not start without `SECRET_KEY`. The `.env` file is excluded from Git.

### 3. Start the development server

```bash
uv run fastapi dev main.py
```

Open the [blog](http://127.0.0.1:8000), [Swagger UI](http://127.0.0.1:8000/docs), or [ReDoc](http://127.0.0.1:8000/redoc).

On startup, the app creates `blog.db` and any missing database tables. The SQLite database lives in the project root and is excluded from Git. Its connection URL is defined in `database.py`.

Register at `/register`, then log in at `/login`. On a fresh database, the first registered user has ID `1`, which the browser currently uses when creating posts.

## Web pages

| Path | Page |
| --- | --- |
| `/` or `/posts` | All posts, newest first. |
| `/posts/{post_id}` | A single post with edit and delete controls for posts by user `1`. |
| `/users/{user_id}/posts` | All posts by an author. |
| `/register` | Account registration. |
| `/login` | Email and password login. |

The browser stores the access token in `localStorage` and uses it to load the current user's profile. Logging out removes the stored token.

## API

### Users

| Method | Endpoint | Action |
| --- | --- | --- |
| `POST` | `/api/users` | Register a user. |
| `POST` | `/api/users/token` | Log in and receive a bearer token. |
| `GET` | `/api/users/me` | Get the current user's profile; requires a bearer token. |
| `GET` | `/api/users/{user_id}` | Get a public profile without the email address. |
| `GET` | `/api/users/{user_id}/posts` | List a user's posts, newest first. |
| `PATCH` | `/api/users/{user_id}` | Update a username, email, or profile image filename. |
| `DELETE` | `/api/users/{user_id}` | Delete a user and their posts. |

Usernames must be 1–50 characters, emails must be valid and at most 120 characters, and passwords must have at least 8 characters. Registration checks usernames and emails for duplicates without regard to case.

### Posts

| Method | Endpoint | Action |
| --- | --- | --- |
| `GET` | `/api/posts` | List all posts, newest first. |
| `POST` | `/api/posts` | Create a post for an existing `user_id`. |
| `GET` | `/api/posts/{post_id}` | Get a post, including its public author profile. |
| `PATCH` | `/api/posts/{post_id}` | Update selected title or content fields. |
| `PUT` | `/api/posts/{post_id}` | Replace the title, content, and author (`user_id`). |
| `DELETE` | `/api/posts/{post_id}` | Delete a post. |

Post titles must be 1–100 characters, and content must not be empty. Successful creation returns `201 Created`; successful deletion returns `204 No Content`.

### Example requests

Register a user:

```bash
curl -X POST http://127.0.0.1:8000/api/users \
  -H 'Content-Type: application/json' \
  -d '{"username":"alex","email":"alex@example.com","password":"example-password-123"}'
```

Log in using form data. The OAuth2 field is named `username`, but its value must be the user's **email address**:

```bash
curl -X POST http://127.0.0.1:8000/api/users/token \
  --data-urlencode 'username=alex@example.com' \
  --data-urlencode 'password=example-password-123'
```

Copy `access_token` from the response and use it to request the current user's profile:

```bash
curl http://127.0.0.1:8000/api/users/me \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

Create a post. Replace `1` with the `id` returned during registration if it differs:

```bash
curl -X POST http://127.0.0.1:8000/api/posts \
  -H 'Content-Type: application/json' \
  -d '{"title":"My first post","content":"Hello from FastAPI!","user_id":1}'
```

You can also try requests in [Swagger UI](http://127.0.0.1:8000/docs). For the protected profile endpoint, select **Authorize** and enter your email in the username field, along with your password.

## Project structure

```text
fastapi-blog/
├── main.py                 # App setup, lifespan, web routes, and error handlers
├── auth.py                 # Password hashing and JWT helpers
├── config.py               # Environment settings
├── database.py             # Async SQLite engine and session dependency
├── models.py               # User and Post database models
├── schemas.py              # Request validation and response schemas
├── routers/
│   ├── users.py            # User and authentication endpoints
│   └── posts.py            # Post endpoints
├── templates/              # Jinja2 pages and shared layout
├── static/                 # CSS, JavaScript, icons, and default profile image
├── media/profile_pics/     # Files served as custom profile images
├── src/fastapi_blog/       # Package and placeholder console command
├── pyproject.toml          # Project metadata and dependencies
└── uv.lock                 # Locked dependency versions
```

## Current limitations

- Only `/api/users/me` requires authentication. User updates and deletions, and post creation, updates, and deletions, currently have no authentication or ownership checks.
- The browser assigns new posts to `user_id = 1` and shows edit/delete buttons only for that user's posts, regardless of who is logged in. User `1` must exist for browser post creation to work.
- Profile images are served from `media/profile_pics/`, with a default image from `static/profile_pics/`. The user update API accepts an `image_file` filename, but there is no file upload endpoint.
- Database tables are created on startup with `create_all`; there are no migration scripts for changing existing tables.
- Post lists are not paginated, and the repository does not yet include an automated test suite.
- The `fastapi-blog` console command only prints a greeting. Start the web app with `uv run fastapi dev main.py`.
