const fs = require('fs');
const path = require('path');
const { ApolloServer } = require('@apollo/server');
const { startStandaloneServer } = require('@apollo/server/standalone');
const { GraphQLError } = require('graphql');
const pool = require('./db');
require('dotenv').config();


const typeDefs = fs.readFileSync(path.join(__dirname, 'schema.graphql'), 'utf8');

const COLUMNS = 'id, name, price, available';

function badInput(message) {
  return new GraphQLError(message, { extensions: { code: 'BAD_USER_INPUT' } });
}

const resolvers = {
  Query: {
    dishes: async (_parent, { available }) => {
      let sql = `SELECT ${COLUMNS} FROM dishes`;
      const params = [];
      if (available !== undefined && available !== null) {
        sql += ' WHERE available = ?';
        params.push(available ? 1 : 0);
      }
      sql += ' ORDER BY id';
      const [rows] = await pool.query(sql, params);
      return rows;
    },

    dish: async (_parent, { id }) => {
      const [rows] = await pool.query(`SELECT ${COLUMNS} FROM dishes WHERE id = ?`, [id]);
      return rows[0] || null;
    },
  },

  Dish: {
    available: (row) => Boolean(row.available),
  },

  Mutation: {
    addDish: async (_parent, { input }) => {
      const name = input.name.trim();
      if (!name) throw badInput('name must not be empty');
      if (input.price <= 0) throw badInput('price must be more than 0');
      const available = input.available ?? true; // the client may skip it

      const [result] = await pool.query(
        'INSERT INTO dishes (name, price, available) VALUES (?, ?, ?)',
        [name, input.price, available ? 1 : 0]
      );
      const [rows] = await pool.query(`SELECT ${COLUMNS} FROM dishes WHERE id = ?`, [result.insertId]);
      return rows[0];
    },
  },
};

async function start() {
  try {
    await pool.query('SELECT 1');
  } catch (err) {
    console.error('Cannot connect to MySQL:', err.message);
    console.error('Check that MySQL is running, schema.sql was loaded, and the password in db.js (or DB_PASSWORD) is right.');
    process.exit(1);
  }

  const server = new ApolloServer({
    typeDefs,
    resolvers,
    includeStacktraceInErrorResponses: false, 
    formatError: (formatted, error) => {
      if (formatted.extensions?.code === 'INTERNAL_SERVER_ERROR') {
        console.error(error);
        return { message: 'Something went wrong on the server.', extensions: { code: 'INTERNAL_SERVER_ERROR' } };
      }
      return formatted;
    },
  });

  const port = Number(process.env.PORT) || 3000;
  const { url } = await startStandaloneServer(server, { listen: { port } });
  console.log(`GraphQL API ready at ${url}`);
}

start();
