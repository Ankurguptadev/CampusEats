const path = require('path');
const express = require('express');

const SEED = [
  { id: 1, name: 'Veg Thali',   price: 90, available: true },
  { id: 2, name: 'Paneer Roll', price: 70, available: true },
  { id: 3, name: 'Cold Coffee', price: 50, available: false },
  { id: 4, name: 'Samosa',  price: 20, available: true },
];

function validate(body) {
  const problems = [];
  if (typeof body.name !== 'string' || !body.name.trim()) {
    problems.push('name is required (non-empty text)');
  }
  if (typeof body.price !== 'number' || !Number.isFinite(body.price) || body.price <= 0) {
    problems.push('price is required (a number above 0)');
  }
  if (body.available !== undefined && typeof body.available !== 'boolean') {
    problems.push('available must be true or false');
  }
  return problems;
}

function createApp() {
  const app = express();
  const items = SEED.map(i => ({ ...i }));
  let nextId = items.length + 1;

  app.use(express.json());                                 
  app.use(express.static(path.join(__dirname, 'public')));  

  app.get('/items', (req, res) => {
    res.json(items);
  });

  app.get('/items/:id', (req, res) => {
    const item = items.find(i => i.id === Number(req.params.id));   
    if (!item) return res.status(404).json({ error: 'item not found' });
    res.json(item);
  });

  app.post('/items', (req, res) => {
    const body = req.body ?? {};            
    const problems = validate(body);
    if (problems.length) {
      return res.status(422).json({ error: 'validation failed', problems });
    }
    const item = {
      id: nextId++,
      name: body.name.trim(),
      price: body.price,
      available: body.available ?? true,
    };
    items.push(item);
    res.status(201).location(`/items/${item.id}`).json(item);
  });

  app.use((req, res) => {
    res.status(404).json({ error: 'not found' });
  });

  app.use((err, req, res, next) => {
    if (err.type === 'entity.parse.failed') {
      return res.status(400).json({ error: 'request body is not valid JSON' });
    }
    console.error(err);
    res.status(500).json({ error: 'server error' });
  });

  return app;
}

module.exports = createApp;

if (require.main === module) {
  const port = process.env.PORT || 3000;
  createApp().listen(port, () => console.log(`Menu API on http://localhost:${port}`));
}
