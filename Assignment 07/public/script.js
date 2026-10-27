const API_URL = "http://localhost:4000";

const dishList = document.getElementById("dish-list");
const message = document.getElementById("message");
const dishForm = document.getElementById("dish-form");
const refreshButton = document.getElementById("refresh-button");
const submitButton = document.getElementById("submit-button");

function showMessage(text, type = "") {
  message.textContent = text;
  message.className = type;
}

async function graphqlRequest(query, variables = {}) {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error: ${response.status}`);
  }

  const result = await response.json();

  if (result.errors?.length) {
    throw new Error(result.errors.map((error) => error.message).join(", "));
  }

  return result.data;
}

function renderDishes(dishes) {
  dishList.innerHTML = "";

  if (!dishes.length) {
    dishList.innerHTML =
      '<p class="empty-state">No dishes found. Add one below.</p>';
    return;
  }

  dishes.forEach((dish) => {
    const card = document.createElement("div");
    card.className = "dish-card";

    const details = document.createElement("div");
    const name = document.createElement("h3");
    const info = document.createElement("p");
    const availability = document.createElement("span");

    name.textContent = dish.name;
    info.textContent = `Dish ID: ${dish.id}`;

    const isAvailable =
      dish.available === true ||
      dish.available === 1 ||
      dish.available === "1" ||
      String(dish.available).toLowerCase() === "true";

    availability.className = isAvailable
      ? "availability"
      : "availability unavailable";

    availability.textContent = isAvailable ? "Available" : "Unavailable";

    details.append(name, info, availability);

    const price = document.createElement("span");
    price.className = "dish-price";
    price.textContent = `₹${Number(dish.price).toLocaleString("en-IN")}`;

    card.append(details, price);
    dishList.appendChild(card);
  });
}

async function loadDishes() {
  refreshButton.disabled = true;
  dishList.textContent = "Loading dishes...";
  showMessage();

  try {
    const data = await graphqlRequest(`
            query {
                dishes {
                    id
                    name
                    price
                    available
                }
            }
        `);

    renderDishes(data.dishes);
  } catch (error) {
    dishList.textContent = "";
    showMessage(`Could not load dishes: ${error.message}`, "error");
  } finally {
    refreshButton.disabled = false;
  }
}

dishForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const name = document.getElementById("dish-name").value.trim();
  const price = Number(document.getElementById("dish-price").value);

  if (!name || !Number.isFinite(price) || price <= 0) {
    showMessage("Enter a valid dish name and price.", "error");
    return;
  }

  submitButton.disabled = true;
  submitButton.textContent = "Adding...";

  try {
    const data = await graphqlRequest(
      `
            mutation AddDish($input: AddDishInput!) {
                addDish(input: $input) {
                    id
                    name
                    price
                }
            }
        `,
      {
        input: { name, price },
      },
    );

    if (!data.addDish) {
      throw new Error("The server did not return the new dish.");
    }

    dishForm.reset();
    await loadDishes();

    showMessage(`${data.addDish.name} added successfully.`, "success");
  } catch (error) {
    showMessage(`Could not add dish: ${error.message}`, "error");
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Add Dish";
  }
});

refreshButton.addEventListener("click", loadDishes);

loadDishes();
