function esc(text) {
  return String(text).replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function showMsg(text, isError = false) {
  const box = document.getElementById('msg');
  box.textContent = text;
  box.className = 'msg ' + (isError ? 'error' : 'ok');
  box.hidden = false;
}

async function load() {
  const list = document.getElementById('list');
  const count = document.getElementById('count');

  try {
    const res = await fetch('/items');
    if (!res.ok) throw new Error(`Request failed (${res.status})`);

    const items = await res.json();
    count.textContent = `${items.length} ${items.length === 1 ? 'item' : 'items'}`;

    if (items.length === 0) {
      list.className = 'empty';
      list.textContent = 'No dishes have been added yet.';
      return;
    }

    list.className = '';
    list.innerHTML = items.map(item => `
      <article class="dish ${item.available ? '' : 'off'}">
        <span class="name">${esc(item.name)}</span>
        <span class="right">
          <span class="badge ${item.available ? 'yes' : 'no'}">${item.available ? 'Available' : 'Sold out'}</span>
          <span class="price">&#8377;${esc(item.price)}</span>
        </span>
      </article>`).join('');
  } catch (error) {
    count.textContent = 'offline';
    list.className = 'empty';
    list.textContent = 'Could not reach the API. Make sure the server is running.';
  }
}

document.getElementById('addForm').addEventListener('submit', async event => {
  event.preventDefault();

  const body = {
    name: document.getElementById('name').value.trim(),
    price: Number(document.getElementById('price').value),
    available: document.getElementById('available').checked,
  };

  try {
    const res = await fetch('/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();

    if (res.status === 201) {
      showMsg(`Added "${data.name}" (ID ${data.id}, status ${res.status}).`);
      event.target.reset();
      document.getElementById('available').checked = true;
      await load();
    } else {
      const details = data.problems || [data.error || 'Please check the submitted details.'];
      showMsg(`Not added (${res.status}): ${details.join(', ')}`, true);
    }
  } catch (error) {
    showMsg('Could not submit the dish. Check that the server is running.', true);
  }
});

load();
