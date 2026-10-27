
require('dotenv').config();

const { ApolloServer } = require('@apollo/server');
const { startStandaloneServer } = require('@apollo/server/standalone');
const pool = require('./db');

// 1. GraphQL schema
const typeDefs = `#graphql
  type Author {
    id: ID!
    name: String!
    country: String
    books: [Book!]!
  }

  type Book {
    id: ID!
    title: String!
    year: Int
    author: Author!
  }

  type Query {
    authors: [Author!]!
    author(id: ID!): Author
    books: [Book!]!
  }

  type Mutation {
    addBook(
      title: String!
      year: Int
      authorName: String!
    ): Book!
  }
`;

// 2. Resolvers
const resolvers = {
  Query: {
    authors: async () => {
      const [rows] = await pool.query(
        'SELECT * FROM authors'
      );

      return rows;
    },

    author: async (_parent, { id }) => {
      const [rows] = await pool.query(
        'SELECT * FROM authors WHERE id = ?',
        [id]
      );

      return rows[0] || null;
    },

    books: async () => {
      const [rows] = await pool.query(
        'SELECT * FROM books'
      );

      return rows;
    },
  },

  // Find books written by an author
  Author: {
    books: async (author) => {
      const [rows] = await pool.query(
        'SELECT * FROM books WHERE author_id = ?',
        [author.id]
      );

      return rows;
    },
  },

  // Find the author of a book
  Book: {
    author: async (book) => {
      const [rows] = await pool.query(
        'SELECT * FROM authors WHERE id = ?',
        [book.author_id]
      );

      return rows[0];
    },
  },

  // Add a book using an author's name
  Mutation: {
    addBook: async (_parent, { title, year, authorName }) => {
      const cleanTitle = title.trim();
      const cleanAuthorName = authorName.trim();

      if (!cleanTitle) {
        throw new Error('Book title cannot be empty');
      }

      if (!cleanAuthorName) {
        throw new Error('Author name cannot be empty');
      }

      // Find the author, ignoring capitalization
      const [existingAuthors] = await pool.query(
        `SELECT * FROM authors
         WHERE LOWER(name) = LOWER(?)
         LIMIT 1`,
        [cleanAuthorName]
      );

      let authorId;

      if (existingAuthors.length > 0) {
        // Reuse the existing author
        authorId = existingAuthors[0].id;
      } else {
        // Create a new author
        const [authorResult] = await pool.query(
          'INSERT INTO authors (name, country) VALUES (?, ?)',
          [cleanAuthorName, null]
        );

        authorId = authorResult.insertId;
      }

      // Insert the book
      const [bookResult] = await pool.query(
        `INSERT INTO books (title, year, author_id)
         VALUES (?, ?, ?)`,
        [
          cleanTitle,
          year ?? null,
          authorId,
        ]
      );

      // Return the newly inserted book
      const [books] = await pool.query(
        'SELECT * FROM books WHERE id = ?',
        [bookResult.insertId]
      );

      return books[0];
    },
  },
};

// 3. Start the GraphQL server
async function start() {
  const server = new ApolloServer({
    typeDefs,
    resolvers,
  });

  const { url } = await startStandaloneServer(server, {
    listen: {
      port: 3000,
    },
  });

  console.log(`GraphQL API ready at ${url}`);
}

start().catch((error) => {
  console.error('Failed to start GraphQL server:', error);
  process.exit(1);
});
