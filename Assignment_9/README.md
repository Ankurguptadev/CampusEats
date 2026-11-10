# CampusEats — Assignment 9: Securing the API

This project extends the CampusEats Catalogue REST service with **JWT authentication** and **role-based authorization**

|Name|Student Id|
|-|:-:|
|Ankur Gupta|20252651008|
|Kartik Karnwal|20252651028|
|Kirti Gautam|20252651029|
|Pintu|20252651038|

**GitHub repo:** https://github.com/Ankurguptadev/CampusEats

**Google Drive :** https://drive.google.com/file/d/1GeSbrRrvBb6acvO1LnnBM0wUYI0ezn6c/view?usp=sharing


## Run locally

Requirements: Node.js 18+ and npm.

```bash
npm install
```

Generate a strong secret and place it in `.env`:

```bash
node -e "console.log(require('crypto').randomBytes(48).toString('hex'))"
```

Then run:

```bash
npm start
```

Open <http://localhost:3000>.

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Customer | `xyz123@gmail.com` | `xyz123` |
| Restaurant | `abc@gmail.com` | `abc123` |

Passwords are hashed with bcrypt when the server starts. The plain-text passwords are only demo credentials documented here; they are not stored in the users array.

## API routes and guards

| Method | Path | Guard | Who can use it |
|---|---|---|---|
| POST | `/login` | Public | Anyone with valid credentials |
| GET | `/health` | Public | Anyone |
| GET | `/me` | `auth` | Any authenticated user |
| GET | `/items` | `auth` | Any authenticated user |
| POST | `/items` | `auth` + `requireRole('restaurant', 'admin')` | Restaurant or admin |
| DELETE | `/items/:id` | `auth` + `requireRole('restaurant', 'admin')` | Restaurant or admin |

The API follows the required order: **authenticate first, then authorize**. A missing/invalid/expired token returns `401`; a valid token with an insufficient role returns `403`.

## Demonstrate the five required cases

Start the server in one terminal. In another terminal:

### 1. No token → 401

```bash
curl -i http://localhost:3000/items
```

### 2. Successful login → token

```bash
RESTAURANT_TOKEN=$(curl -s -X POST http://localhost:3000/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"mealhub@campus.edu","password":"resto123"}' \
  | node -pe "JSON.parse(require('fs').readFileSync(0,'utf8')).token")
echo "$RESTAURANT_TOKEN"
```

### 3. Valid token → 200

```bash
curl -i http://localhost:3000/items \
  -H "Authorization: Bearer $RESTAURANT_TOKEN"
```

### 4. Restaurant role writes → 201

```bash
curl -i -X POST http://localhost:3000/items \
  -H "Authorization: Bearer $RESTAURANT_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Masala Dosa","price":80}'
```

### 5. Customer role writes → 403

```bash
CUSTOMER_TOKEN=$(curl -s -X POST http://localhost:3000/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"asha@campus.edu","password":"customer123"}' \
  | node -pe "JSON.parse(require('fs').readFileSync(0,'utf8')).token")

curl -i -X POST http://localhost:3000/items \
  -H "Authorization: Bearer $CUSTOMER_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test Dish","price":50}'
```

## Answers for the README questions

1. **Which routes require authentication and which also require a role?**  
   `GET /me` and `GET /items` require authentication only. `POST /items` and `DELETE /items/:id` require authentication plus the `restaurant` or `admin` role. `POST /login` and `GET /health` are public.

2. **Show one 401 and one 403.**  
   `GET /items` without a token returns `401` because the server cannot authenticate the caller. `POST /items` with a valid customer token returns `403` because the caller is authenticated but does not have permission to add menu items.

3. **What is inside the JWT payload, and why is it safe to trust the role?**  
   The payload contains `sub` (user id), `role`, and `name`; the token also has an expiry (`exp`) added by `jsonwebtoken`. The server verifies the token signature using the secret before reading the role, so changing the role invalidates the signature. The secret must stay outside source code because anyone who obtains it can create valid tokens.

## Note

Please check the curl_test_result.txt for the testing part of the API's