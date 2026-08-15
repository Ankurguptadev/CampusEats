# CampusEats — The Simple Guide

## 1. What is CampusEats?
CampusEats is an app that lets hungry students on a school campus order food from nearby restaurants and get it delivered right to their doorstep by a delivery rider, while sending updates at every step.

## 2. Who Uses It?
*   **Students:** The hungry buyers who log in, pick out food, pay for it, and wait for their meal.
*   **Restaurants:** The kitchens that make the food, show their menus, and list their prices.
*   **Riders:** The delivery helpers who pick up the food from the kitchen and bring it to the student.

## 3. The Nouns
Think of the app as a giant food court with 6 specialized teams. Each team has its own private lockbox of information and never shares its keys with anyone else:

*   **The Accounts Team:** Keeps track of who you are, your password, and your delivery address.
*   **The Catalogue Team:** Holds the master menu list of every restaurant, what dishes they make, and how much they cost.
*   **The Orders Team:** Watches your shopping cart, knows exactly what you decided to buy right now, and tracks if your meal is being made.
*   **The Payments Team:** Handles the money, charges your card, and handles refunds if something goes wrong.
*   **The Delivery Team:** Finds an available rider with a bike, tells them where to go, and keeps an eye on where they are on the map.
*   **The Notifications Team:** Writes out and sends the alert messages to your phone (like "Your food is on the way!").

## 4. The Verbs (The Actions & Commands They Do)
These are the specific tasks that the users perform, or the instructions the teams send to each other to get your food delivered. Each one also comes with a promise: what you get back if it works, and what can go wrong if it doesn't.

*   **Accounts Actions:**
    *   `login`: Lets you into the app.
    *   `manageProfile`: Changes your phone number or saves a new dorm room address.

*   **Catalogue Actions:**
    *   `listRestaurants`: Shows you a list of open places to eat nearby.
    *   `getMenu`: Opens up a restaurant's digital menu so you can see the food.
    *   `checkItem`: Checks if a kitchen has enough ingredients left to make a specific burger or pizza, and checks its price. Comes back empty-handed if the item can't be found.

*   **Orders Actions:**
    *   `addToCart`: Throws a food item into your digital basket. Fails if that item just went unavailable.
    *   `placeOrder`: Officially tells the kitchen to start cooking your food basket, and hands you back an order number, a status, and a total. Fails if your cart is empty or your address is bad.
    *   `getOrder`: Checks the status screen to see if your food is ready.
    *   `cancelOrder`: Stops the cooking if you change your mind quickly — but only if you're fast enough, since it can be too late to cancel.

*   **Payments Actions:**
    *   `charge`: Takes the money from your bank account to pay for the meal. Fails if the card gets declined.
    *   `refund`: Puts the money back in your pocket if the kitchen runs out of cheese.

*   **Delivery Actions:**
    *   `assignRider`: Finds a rider and hands them the map to your building.
    *   `trackDelivery`: Lets you watch on a map where your rider is and how close they are to your door.

*   **Notifications Actions:**
    *   `send`: Pops a message onto your phone screen so you know the rider is outside.