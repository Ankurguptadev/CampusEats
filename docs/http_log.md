# HTTP Log

## Request 1 — GET Users 1

### Request

```sh
curl -i https://jsonplaceholder.typicode.com/users/1
```

### Response

```text
HTTP/2 200 
date: Sat, 15 Aug 2026 11:36:15 GMT
content-type: application/json; charset=utf-8
content-length: 509
access-control-allow-credentials: true
cache-control: max-age=43200
etag: W/"1fd-+2Y3G3w049iSZtw5t1mzSnunngE"
expires: -1
nel: {"report_to":"heroku-nel","response_headers":["Via"],"max_age":3600,"success_fraction":0.01,"failure_fraction":0.1}
pragma: no-cache
report-to: {"group":"heroku-nel","endpoints":[{"url":"https://nel.heroku.com/reports?s=GIwyebBgV7ZP9c3UF77flf3I4W3a8sXS5tSGoy7EShQ%3D\u0026sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d\u0026ts=1786526571"}],"max_age":3600}
reporting-endpoints: heroku-nel="https://nel.heroku.com/reports?s=GIwyebBgV7ZP9c3UF77flf3I4W3a8sXS5tSGoy7EShQ%3D&sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d&ts=1786526571"
server: cloudflare
vary: Origin, Accept-Encoding
via: 2.0 heroku-router
x-content-type-options: nosniff
x-powered-by: Express
x-ratelimit-limit: 1000
x-ratelimit-remaining: 999
x-ratelimit-reset: 1786526575
age: 6663
accept-ranges: bytes
cf-cache-status: HIT
cf-ray: a2b7e6881a423afb-BOM
alt-svc: h3=":443"; ma=86400

{
  "id": 1,
  "name": "Leanne Graham",
  "username": "Bret",
  "email": "Sincere@april.biz",
  "address": {
    "street": "Kulas Light",
    "suite": "Apt. 556",
    "city": "Gwenborough",
    "zipcode": "92998-3874",
    "geo": {
      "lat": "-37.3159",
      "lng": "81.1496"
    }
  },
  "phone": "1-770-736-8031 x56442",
  "website": "hildegard.org",
  "company": {
    "name": "Romaguera-Crona",
    "catchPhrase": "Multi-layered client-server neural-net",
    "bs": "harness real-time e-markets"
  }
}  
```
**Status:** `200` means the server successfully processed the request and returned the requested resource.
**Content-Type:** `application/json; charset=utf-8` means the response is JSON data encoded using UTF-8.



## Request 2 — GET Posts 1

### Request

```sh
curl -i https://jsonplaceholder.typicode.com/posts/1
```

### Response

```text
HTTP/2 200 
date: Sat, 15 Aug 2026 11:38:08 GMT
content-type: application/json; charset=utf-8
content-length: 292
access-control-allow-credentials: true
cache-control: max-age=43200
etag: W/"124-yiKdLzqO5gfBrJFrcdJ8Yq0LGnU"
expires: -1
nel: {"report_to":"heroku-nel","response_headers":["Via"],"max_age":3600,"success_fraction":0.01,"failure_fraction":0.1}
pragma: no-cache
report-to: {"group":"heroku-nel","endpoints":[{"url":"https://nel.heroku.com/reports?s=vm67FVLNHsCgrFgubRa04ooDeMKdgwXS9H3i2IbjuoY%3D\u0026sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d\u0026ts=1785194657"}],"max_age":3600}
reporting-endpoints: heroku-nel="https://nel.heroku.com/reports?s=vm67FVLNHsCgrFgubRa04ooDeMKdgwXS9H3i2IbjuoY%3D&sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d&ts=1785194657"
server: cloudflare
vary: Origin, Accept-Encoding
via: 2.0 heroku-router
x-content-type-options: nosniff
x-powered-by: Express
x-ratelimit-limit: 1000
x-ratelimit-remaining: 999
x-ratelimit-reset: 1785194663
age: 36
accept-ranges: bytes
cf-cache-status: HIT
cf-ray: a2b7e9492fd13d24-BOM
alt-svc: h3=":443"; ma=86400

{
  "userId": 1,
  "id": 1,
  "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
  "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nreprehenderit molestiae ut ut quas totam\nnostrum rerum est autem sunt rem eveniet architecto"
}
```
**Status:** `200` means the server successfully processed the request and returned the requested resource.
**Content-Type:** `application/json; charset=utf-8` means the response is JSON data encoded using UTF-8.


## Request 3 — POST posts 

### Request

```sh
curl -i -X POST -H "Content-Type: application/json" -d '{"title": "foo"}' https://jsonplaceholder.typicode.com/posts
```

### Response

```text
HTTP/2 201 
date: Sat, 15 Aug 2026 11:12:56 GMT
content-type: application/json; charset=utf-8
content-length: 33
location: https://jsonplaceholder.typicode.com/posts/101
access-control-allow-credentials: true
access-control-expose-headers: Location
cache-control: no-cache
etag: W/"21-th+xRuBjwnxqhHZKd1wbIPhi8IU"
expires: -1
nel: {"report_to":"heroku-nel","response_headers":["Via"],"max_age":3600,"success_fraction":0.01,"failure_fraction":0.1}
pragma: no-cache
report-to: {"group":"heroku-nel","endpoints":[{"url":"https://nel.heroku.com/reports?s=ylzXKLXWyNMbqyeBrtqwRrgLaMxlIulLltbkE4ngopA%3D\u0026sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d\u0026ts=1786792376"}],"max_age":3600}
reporting-endpoints: heroku-nel="https://nel.heroku.com/reports?s=ylzXKLXWyNMbqyeBrtqwRrgLaMxlIulLltbkE4ngopA%3D&sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d&ts=1786792376"
server: cloudflare
vary: Origin, X-HTTP-Method-Override, Accept-Encoding
via: 2.0 heroku-router
x-content-type-options: nosniff
x-powered-by: Express
x-ratelimit-limit: 1000
x-ratelimit-remaining: 999
x-ratelimit-reset: 1786792423
cf-cache-status: DYNAMIC
cf-ray: a2b7c462583774eb-BOM
alt-svc: h3=":443"; ma=86400

{
  "title": "foo",
  "id": 101
}
```
**Status:** `201` means the server successfully processed the request and created a new resource.
**Content-Type:** `application/json; charset=utf-8` means the response is JSON data encoded using UTF-8.



## Request 4 — GET Google Redirect

### Request

```sh
curl -I http://google.com
```

### Response

```text
HTTP/1.1 301 Moved Permanently
Location: http://www.google.com/
Content-Type: text/html; charset=UTF-8
Content-Security-Policy-Report-Only: object-src 'none';base-uri 'self';script-src 'nonce-bu2NuhXe4SBIHX4062WgyA' 'strict-dynamic' 'report-sample' 'unsafe-eval' 'unsafe-inline' https: http:;report-uri https://csp.withgoogle.com/csp/gws/other-hp
Date: Sat, 15 Aug 2026 11:19:02 GMT
Expires: Mon, 14 Sep 2026 11:19:02 GMT
Cache-Control: public, max-age=2592000
Server: gws
Content-Length: 219
X-XSS-Protection: 0
X-Frame-Options: SAMEORIGIN
```
**Status:** `301` means the requested resource has been assigned a new permanent URL.
**Content-Type:** `text/html; charset=UTF-8` means the response is text or HTML data encoded using UTF-8.



## Request 5 — GET Photos 5555

### Request

```sh
curl -i https://jsonplaceholder.typicode.com/photos/5555
```

### Response

```text
HTTP/2 404 
date: Sat, 15 Aug 2026 11:49:30 GMT
content-type: application/json; charset=utf-8
content-length: 2
access-control-allow-credentials: true
cache-control: max-age=43200
etag: W/"2-vyGp6PvFo4RvsFtPoIWeCReyIC8"
expires: -1
nel: {"report_to":"heroku-nel","response_headers":["Via"],"max_age":3600,"success_fraction":0.01,"failure_fraction":0.1}
pragma: no-cache
report-to: {"group":"heroku-nel","endpoints":[{"url":"https://nel.heroku.com/reports?s=UXkgokLRhahNQZ4Fd6RiEarUReFkfhRfTsd61nOaIyI%3D\u0026sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d\u0026ts=1786794570"}],"max_age":3600}
reporting-endpoints: heroku-nel="https://nel.heroku.com/reports?s=UXkgokLRhahNQZ4Fd6RiEarUReFkfhRfTsd61nOaIyI%3D&sid=e11707d5-02a7-43ef-b45e-2cf4d2036f7d&ts=1786794570"
server: cloudflare
vary: Origin, Accept-Encoding
via: 2.0 heroku-router
x-content-type-options: nosniff
x-powered-by: Express
x-ratelimit-limit: 1000
x-ratelimit-remaining: 999
x-ratelimit-reset: 1786794583
cf-cache-status: MISS
cf-ray: a2b7f9ee99ab4817-BOM
alt-svc: h3=":443"; ma=86400

{}
```
**Status:** `404` means the requested resource does not exist on the server.
**Content-Type:** `application/json; charset=utf-8` means the response is JSON data encoded using UTF-8.