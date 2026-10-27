require('dotenv').config();
const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: process.env.DB_PASSWORD ?? 'YOUR_MYSQL_PASSWORD', // <-- change this, or set DB_PASSWORD
  database: 'library',
});

module.exports = pool;
