const API = "";
const loginPanel = document.getElementById("login-panel");
const cataloguePanel = document.getElementById("catalogue-panel");
const loginForm = document.getElementById("login-form");
const addForm = document.getElementById("add-form");
const itemsList = document.getElementById("items-list");
const notice = document.getElementById("notice");
const sessionLabel = document.getElementById("session-label");
const logoutButton = document.getElementById("logout-button");

let token = sessionStorage.getItem("campuseats_token") || "";
let currentUser = null;

try {
  const storedUser = sessionStorage.getItem("campuseats_user");

  if (storedUser && storedUser !== "undefined") {
    currentUser = JSON.parse(storedUser);
  }
} catch (error) {
  console.error("Error restoring session:", error);
  sessionStorage.removeItem("campuseats_token");
  sessionStorage.removeItem("campuseats_user");

  token = "";
  currentUser = null;
}

function showNotice(message, isError = false) {
  notice.textContent = message;
  notice.classList.remove("hidden", "error");

  if (isError) {
    notice.classList.add("error");
  }
}

function clearNotice() {
  notice.classList.add("hidden");
  notice.textContent = "";
}

async function apiRequest(path, options = {}) {
  const headers = {
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  if (options.body) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API}${path}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const error = new Error(
      data.error || `Request failed (${response.status})`,
    );

    error.status = response.status;
    throw error;
  }

  return data;
}

function setSignedIn(user, jwt) {
  if (!user || !jwt) {
    throw new Error("Invalid login response from server");
  }

  currentUser = user;
  token = jwt;

  sessionStorage.setItem("campuseats_token", token);
  sessionStorage.setItem("campuseats_user", JSON.stringify(currentUser));

  renderSession();
}

function signOut() {
  token = "";
  currentUser = null;

  sessionStorage.removeItem("campuseats_token");
  sessionStorage.removeItem("campuseats_user");

  renderSession();
}

function renderSession() {
  const signedIn = Boolean(token && currentUser);

  loginPanel.classList.toggle("hidden", signedIn);
  cataloguePanel.classList.toggle("hidden", !signedIn);
  logoutButton.classList.toggle("hidden", !signedIn);

  sessionLabel.textContent = signedIn
    ? `${currentUser.name} · ${currentUser.role}`
    : "Not signed in";

  addForm.classList.toggle(
    "hidden",
    !signedIn || currentUser.role !== "restaurant",
  );

  if (signedIn) {
    loadItems();
  }
}

function renderItems(items) {
  itemsList.replaceChildren();

  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "hint";
    empty.textContent = "No menu items available yet.";

    itemsList.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "item-card";

    const details = document.createElement("div");

    const name = document.createElement("p");
    name.className = "item-name";
    name.textContent = item.name;

    const id = document.createElement("span");
    id.className = "item-id";
    id.textContent = `Menu item #${item.id}`;

    const availability = document.createElement("span");
    availability.className = "item-id";
    availability.textContent = item.available ? "Available" : "Unavailable";

    details.append(name, id, availability);

    const actions = document.createElement("div");

    const price = document.createElement("span");
    price.className = "item-price";
    price.textContent = `₹${Number(item.price).toFixed(2)}`;

    actions.appendChild(price);

    if (currentUser && currentUser.role === "restaurant") {
      const remove = document.createElement("button");

      remove.className = "delete-button";
      remove.type = "button";
      remove.textContent = "Remove";

      remove.addEventListener("click", () => {
        deleteItem(item.id);
      });

      actions.appendChild(remove);
    }

    card.append(details, actions);
    itemsList.appendChild(card);
  });
}

async function loadItems() {
  clearNotice();

  try {
    const items = await apiRequest("/items");
    renderItems(items);
  } catch (error) {
    showNotice(error.message, true);

    if (error.status === 401) {
      signOut();
    }
  }
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearNotice();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try {
    const result = await apiRequest("/login", {
      method: "POST",
      body: JSON.stringify({
        email,
        password,
      }),
    });

    if (!result.token || !result.user) {
      throw new Error("Invalid login response from server");
    }

    setSignedIn(result.user, result.token);

    loginForm.reset();
  } catch (error) {
    let message = loginPanel.querySelector(".login-error");

    if (!message) {
      message = document.createElement("p");
      message.className = "hint login-error";
      loginForm.after(message);
    }

    message.textContent = error.message;
    message.style.color = "#ff9c9c";
  }
});

addForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearNotice();

  const nameInput = document.getElementById("item-name");
  const priceInput = document.getElementById("item-price");

  try {
    await apiRequest("/items", {
      method: "POST",
      body: JSON.stringify({
        name: nameInput.value.trim(),
        price: Number(priceInput.value),
      }),
    });

    addForm.reset();

    showNotice("Menu item added successfully.");

    await loadItems();
  } catch (error) {
    showNotice(error.message, true);
  }
});

async function deleteItem(id) {
  if (!window.confirm("Remove this menu item?")) {
    return;
  }

  try {
    await apiRequest(`/items/${id}`, {
      method: "DELETE",
    });

    showNotice("Menu item removed successfully.");

    await loadItems();
  } catch (error) {
    showNotice(error.message, true);
  }
}

document.getElementById("refresh-button").addEventListener("click", loadItems);

logoutButton.addEventListener("click", signOut);

if (!token || !currentUser) {
  token = "";
  currentUser = null;

  sessionStorage.removeItem("campuseats_token");
  sessionStorage.removeItem("campuseats_user");
}

renderSession();
