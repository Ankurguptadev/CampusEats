# Campus Library

A simple library management application built using Node.js, GraphQL, and MySQL.

## Features

- View books and their authors.
- Add new books.
- Enter author names manually.
- Automatically create new authors if they do not exist.
- Store book and author details in MySQL.

## Technologies Used

- Node.js
- Apollo Server
- GraphQL
- MySQL
- HTML
- CSS
- JavaScript

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure the Database

Run the following command from the project root:

```bash
mysql -u root -p < schema.sql
```

Enter your MySQL password when prompted.

**Note:** The SQL file drops and recreates the `authors` and `books` tables. Existing data in those tables will be deleted.

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_PASSWORD=your_mysql_password
```

Replace `your_mysql_password` with your actual MySQL password.

### 4. Start the Server

```bash
npm start
```

The GraphQL API will be available at:

http://localhost:3000/

### 5. Open the Application

Open `public/index.html` in your browser to use the library application.

## Project Structure

```text
campus-library/
├── public/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── db.js
├── server.js
├── schema.sql
├── package.json
├── package-lock.json
├── .env
└── README.md
```

## Database Schema

### Authors Table

Stores author information:

- `id`: Unique author ID
- `name`: Author's name

### Books Table

Stores book information:

- `id`: Unique book ID
- `title`: Book title
- `year`: Publication year
- `author_id`: ID of the book's author

One author can have multiple books.

## License

This project is intended for educational purposes.