const path = require("path");
const express = require("express");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcryptjs");
require("dotenv").config();
const SECRET = process.env.JWT_SECRET;

const SEED = [
  { id: 1, name: "Veg Thali", price: 90, available: true },
  { id: 2, name: "Paneer Roll", price: 70, available: true },
  { id: 3, name: "Cold Coffee", price: 50, available: false },
  { id: 4, name: "Samosa", price: 20, available: true },
];

function validate(body) {
  const problems = [];

  if (typeof body.name !== "string" || !body.name.trim()) {
    problems.push("name is required (non-empty text)");
  }

  if (
    typeof body.price !== "number" ||
    !Number.isFinite(body.price) ||
    body.price <= 0
  ) {
    problems.push("price is required (a number above 0)");
  }

  if (
    body.available !== undefined &&
    typeof body.available !== "boolean"
  ) {
    problems.push("available must be true or false");
  }

  return problems;
}

function createApp() {
  const app = express();

  const items = SEED.map((item) => ({ ...item }));
  let nextId = items.length + 1;

  const users = [
    {
      id: 1,
      email: "xyz123@gmail.com",
      name: "XYZ",
      role: "customer",
      hash: bcrypt.hashSync("xyz123", 10),
    },
    {
      id: 2,
      email: "abc@gmail.com",
      name: "ABC",
      role: "restaurant",
      hash: bcrypt.hashSync("abc123", 10),
    },
  ];

  app.use(express.json());
  app.use(express.static(path.join(__dirname, "public")));

  // Login route
  app.post("/login", (req, res) => {
    const body = req.body ?? {};

    const user = users.find(
      (u) => u.email === body.email
    );

    if (
      !user ||
      !bcrypt.compareSync(body.password || "", user.hash)
    ) {
      return res.status(401).json({
        error: "Invalid email or password",
      });
    }

    const token = jwt.sign(
      {
        sub: user.id,
        role: user.role,
      },
      SECRET,
      {
        expiresIn: "1h",
      }
    );

    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
      },
    });
  });

  function auth(req, res, next) {
    const header = req.get("Authorization") || "";
    const parts = header.split(" ");

    if (
      parts.length !== 2 ||
      parts[0] !== "Bearer" ||
      !parts[1]
    ) {
      return res.status(401).json({
        error: "Invalid or missing token",
      });
    }

    try {
      req.user = jwt.verify(parts[1], SECRET);
      next();
    } catch (error) {
      return res.status(401).json({
        error: "Invalid or expired token",
      });
    }
  }

  function requireRole(...allowedRoles) {
    return (req, res, next) => {
      if (!allowedRoles.includes(req.user.role)) {
        return res.status(403).json({
          error: "Forbidden: insufficient permissions",
        });
      }

      next();
    };
  }

  app.get("/items", auth, (req, res) => {
    res.json(items);
  });

  app.get("/items/:id", auth, (req, res) => {
    const item = items.find(
      (i) => i.id === Number(req.params.id)
    );

    if (!item) {
      return res.status(404).json({
        error: "Item not found",
      });
    }

    res.json(item);
  });

  app.post(
    "/items",
    auth,
    requireRole("restaurant", "admin"),
    (req, res) => {
      const body = req.body ?? {};
      const problems = validate(body);

      if (problems.length) {
        return res.status(422).json({
          error: "Validation failed",
          problems,
        });
      }

      const item = {
        id: nextId++,
        name: body.name.trim(),
        price: body.price,
        available: body.available ?? true,
      };

      items.push(item);

      res
        .status(201)
        .location(`/items/${item.id}`)
        .json(item);
    }
  );

  app.delete(
    "/items/:id",
    auth,
    requireRole("restaurant", "admin"),
    (req, res) => {
      const index = items.findIndex(
        (i) => i.id === Number(req.params.id)
      );

      if (index === -1) {
        return res.status(404).json({
          error: "Item not found",
        });
      }

      items.splice(index, 1);

      res.json({
        message: "Item deleted successfully",
      });
    }
  );

  app.use((req, res) => {
    res.status(404).json({
      error: "Not found",
    });
  });

  app.use((err, req, res, next) => {
    if (err.type === "entity.parse.failed") {
      return res.status(400).json({
        error: "Request body is not valid JSON",
      });
    }

    console.error(err);

    res.status(500).json({
      error: "Server error",
    });
  });

  return app;
}

module.exports = createApp;

if (require.main === module) {
  const port = process.env.PORT || 3000;

  createApp().listen(port, () => {
    console.log(`Secured Menu API running at http://localhost:${port}`);
  });
}
