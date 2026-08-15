# Assignments in This Submission

This submission bundles three separate tasks:

1. **`brief.md`** — CampusEats service boundaries brief (CS543 Tutorial 2)
2. **`http_log.md`** — `curl -i`, 5 public requests, including one 404
3. **`network_analysis.md`** — browser DevTools network waterfall analysis

The sections below describe assignment 1 (`brief.md`) in detail.

---

# CampusEats — Service Boundaries Brief

## About
This repo contains a one-page brief on **CampusEats**, a sample food-delivery
project used in *CS543(Web Services) Tutorial 2* to teach how to break a
monolithic app into well-bounded services.

The brief explains the system in plain language: what it does, who uses it,
its **nouns** (the services and the data each one owns), and its **verbs**
(the actions/contracts each service exposes to the rest of the system).

## Files
| File | Description |
|---|---|
| `brief.md` | The one-page CampusEats brief — what / who / nouns / verbs |

## Source
Based on the CampusEats example from *CS543 Tutorial 2: Drawing Service
Boundaries* slides, which walks through the
four-step methodology: **find the capabilities → group by data ownership →
draw the boundaries → define the contracts.**

## How to Read the Brief
1. **What** — a two-sentence description of the whole system.
2. **Who** — the people/roles that use it (students, restaurants, riders).
3. **Nouns** — the six services, each owning its own private slice of data
   (Accounts, Catalogue, Orders, Payments, Delivery, Notifications).
4. **Verbs** — the operations each service exposes, along with what you get
   back and what can go wrong (its contract).

## Key Idea
Every service owns its own data and is only ever called through its
published contract — never by another service reaching directly into its
database. That's what keeps CampusEats loosely coupled and easy to change.