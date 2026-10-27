
const API = 'http://localhost:3000/';

const list = document.getElementById('list');
const summary = document.getElementById('summary');
const form = document.getElementById('addForm');
const formMessage = document.getElementById('formMessage');

// Send a GraphQL request and report useful error messages
async function gql(query, variables = {}) {
  const response = await fetch(API, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query,
      variables
    })
  });

  const result = await response.json();

  if (!response.ok || result.errors?.length) {
    const message = result.errors
      ?.map(error => error.message)
      .join('\n');

    throw new Error(
      message || `HTTP ${response.status}: ${JSON.stringify(result)}`
    );
  }

  return result.data;
}

// Escape HTML before displaying database values
function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[char]));
}

// Load books grouped by author
async function load() {
  list.innerHTML = `
    <div class="state-card">
      <span class="loader" aria-hidden="true"></span>
      <p>Loading books...</p>
    </div>
  `;

  try {
    const data = await gql(`
      query {
        authors {
          id
          name
          books {
            id
            title
            year
          }
        }
      }
    `);

    const authors = data.authors || [];

    const bookCount = authors.reduce(
      (total, author) => total + (author.books?.length || 0),
      0
    );

    summary.textContent =
      `${bookCount} ${bookCount === 1 ? 'book' : 'books'} · ` +
      `${authors.length} ${authors.length === 1 ? 'author' : 'authors'}`;

    if (authors.length === 0) {
      list.innerHTML = `
        <div class="state-card">
          <h3>Your collection is empty</h3>
          <p>Add a book to get started.</p>
        </div>
      `;
      return;
    }

    list.innerHTML = authors.map(author => {
      const books = author.books || [];

      return `
        <article class="author-card">
          <div class="author-head">
            <div class="author-avatar" aria-hidden="true">
              ${escapeHTML(
                (author.name || '?').trim().charAt(0).toUpperCase()
              )}
            </div>

            <div>
              <h3>${escapeHTML(author.name)}</h3>
              <p class="author-meta">Author</p>
            </div>
          </div>

          <div class="books-heading">
            <span>BOOKS</span>
            <span class="book-count">${books.length}</span>
          </div>

          ${
            books.length
              ? `
                <ul class="book-list">
                  ${books.map(book => `
                    <li class="book-item">
                      <span class="book-title">
                        ${escapeHTML(book.title)}
                      </span>

                      <span class="book-year">
                        ${book.year != null
                          ? escapeHTML(book.year)
                          : '—'}
                      </span>
                    </li>
                  `).join('')}
                </ul>
              `
              : '<p class="no-books">No books added yet.</p>'
          }
        </article>
      `;
    }).join('');

  } catch (error) {
    console.error('Could not load books:', error);

    summary.textContent = 'Could not load collection';

    list.innerHTML = `
      <div class="state-card">
        <h3>Unable to load books</h3>
        <p>${escapeHTML(error.message)}</p>
        <button type="button" id="retryButton">Try again</button>
      </div>
    `;

    document.getElementById('retryButton')
      ?.addEventListener('click', load);
  }
}

// Add a book using a typed author name
form.addEventListener('submit', async event => {
  event.preventDefault();

  const button = form.querySelector('button[type="submit"]');

  // These IDs must match index.html
  const title = document.getElementById('title').value.trim();
  const authorName = document.getElementById('author').value.trim();
  const yearValue = document.getElementById('year').value.trim();

  if (!title || !authorName) {
    formMessage.textContent = 'Please enter a book title and author name.';
    formMessage.className = 'form-message failure';
    return;
  }

  const year = yearValue === '' ? null : Number(yearValue);

  if (
    year !== null &&
    (!Number.isInteger(year) || year < 0 || year > 2100)
  ) {
    formMessage.textContent = 'Please enter a valid publication year.';
    formMessage.className = 'form-message failure';
    return;
  }

  button.disabled = true;
  button.textContent = 'Adding book...';

  formMessage.textContent = '';
  formMessage.className = 'form-message';

  try {
    const mutation = `
      mutation (
        $title: String!,
        $year: Int,
        $authorName: String!
      ) {
        addBook(
          title: $title,
          year: $year,
          authorName: $authorName
        ) {
          id
          title
          year
          author {
            id
            name
          }
        }
      }
    `;

    await gql(mutation, {
      title,
      year,
      authorName
    });

    form.reset();

    formMessage.textContent = 'Book added successfully.';
    formMessage.className = 'form-message success';

    await load();

  } catch (error) {
    console.error('Could not add book:', error);

    formMessage.textContent =
      `Could not add the book: ${error.message}`;

    formMessage.className = 'form-message failure';

  } finally {
    button.disabled = false;
    button.innerHTML =
      '<span>Add book</span><span aria-hidden="true">→</span>';
  }
});

// Load the collection when the page opens
load();