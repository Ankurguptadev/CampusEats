# CampusEats Menu - REST API with Node \& Express (Assignment 8)

|Name|Student Id|
|-|:-:|
|Ankur Gupta|20252651008|
|Kartik Karnwal|20252651028|
|Kirti Gautam|20252651029|
|Pintu|20252651038|

**GitHub repo:** https://github.com/KartikKarnwal1714/CampusEats

**Google Drive :** https://drive.google.com/drive/folders/1ATTPUi8JIIDLtE-CNEwvPux0-IeucHQR?usp=sharing

## How to run it

One line: `npm install`, then `npm start`, then open http://localhost:3000 in the browser.

```
npm install
npm start          # prints: Menu API on http://localhost:3000

```

Open **http://localhost:3000** (not the HTML file directly, the page talks to the server on the same address). Needs Node 18 or newer. The data is in memory, so it resets every time the server restarts.

## Before and after the POST

|Before (5 items)|After adding "Dosa" (6 items)|
|-|-|
|!\[before](screenshots/before.png)|!\[after](screenshots/after.png)|

## What is in the repo

|File|What it is|
|-|-|
|`server.js`|the Express REST API: the three routes and the 4 seed records|
|`package.json`|lists `express` as a dependency|
|`public/index.html`, `public/style.css`|the page: lists the menu, one form adds a dish|

## Answers

**1. Which CampusEats service did you pick, and what are its routes?**
The **Menu (Catalogue)**. Each item has `id`, `name`, `price` and `available`.

|Method|Path|What it does|
|-|-|-|
|GET|`/items`|list every item|
|GET|`/items/:id`|one item|
|POST|`/items`|add an item|

**2. Which status codes did you return, and for which outcomes?**

|Code|When|
|-|-|
|**200** OK|`GET /items` and `GET /items/:id` found what was asked for|
|**201** Created|`POST /items` worked. The reply is the new item, and a `Location: /items/5` header points to it|
|**404** Not Found|`GET /items/999` (no item with that id). Also any URL that doesn't exist|
|**422** Unprocessable Entity|`POST /items` with a missing or bad `name` or `price`. The reply lists every problem|
|400 Bad Request|(extra) the body is not valid JSON at all|

**3. Where did you use `req.params` and where `req.body`? Why does POST need `express.json()`?**

* `req.params` is in **`GET /items/:id`**: `req.params.id` is the id taken from the URL (`/items/2` gives `"2"`, and I turn it into a number to find the item).
* `req.body` is in **`POST /items`**: it holds the JSON the client sent (`{"name": "Masala Dosa", "price": 60}`), which I check and then save.
* POST needs `express.json()` because Express does not read the body by itself. The body arrives as plain text; `express.json()` turns it into a JavaScript object and puts it in `req.body`. Without it, `req.body` is `undefined` (in Express 5), so the server could never see the `name` and `price`.

