# 🛡️ Insurance4You Management System

**Insurance4You** is a console-based insurance management system built in Python. It simulates a real-world insurance application with three distinct user roles (Customer, Agent, and Administrator), each with a dedicated menu and set of permissions.

This system was developed as a group project (4 members) for the **TMF2243 Object Oriented Software Engineering** course during Semester 3 at **Universiti Malaysia Sarawak (UNIMAS)**.

## ✨ Key Features

* **Role-Based Access Control:** Separate menus and functionality for Customers, Agents, and Administrators.
* **Full User Management:** Secure registration and login for all three user roles.
* **Policy Management:** Customers can browse and purchase standard policies (Life, Vehicle, Health, Property).
* **Policy Customization:** A dynamic-yet-simple system for customers to create custom policies with specific coverage, which are then queued for admin approval.
* **Claims Processing:** Customers can file claims on their active policies, which admins can then review, approve, or reject.
* **Agent Dashboard:** Agents can manage their customer policies, track sales, and automatically calculate their commissions.
* **Admin Panel:** Administrators have oversight to manage agents, generate sales reports, and validate all pending claims and custom policies.
* **Persistent Storage:** Uses SQLite3 to store all user, policy, claim, and payment data.

---

## 🚀 How to Run

1.  Ensure you have Python 3 installed.
2.  Run the `database_setup.py` script **once** to create the `insurance_system.db` database and populate it with test data:
    ```bash
    python database_setup.py
    ```
3.  Run the main application:
    ```bash
    python main.py
    ```
4.  You can log in using the test data provided in `database_setup.py`.

### Test Login Credentials

* **Customer:**
    * **ID:** `970521125566`
    * **Password:** `jake123`
* **Agent:**
    * **ID:** `041210150087`
    * **Password:** `nsofea123`
* **Administrator:**
    * **ID:** `950730134677`
    * **Password:** `admingrace`

---

## 🧑‍🤝‍🧑 User Roles & Functionality

The system is divided into three main roles:

### 👤 Customer
* Register and manage their personal profile.
* Browse and purchase pre-defined insurance plans (Standard, Premium).
* Create and submit custom insurance policies with calculated premiums.
* View the status of all purchased policies (Pending, Accepted, Rejected, etc.).
* File a claim against an active policy.
* Make payments for policies.
* Cancel an existing policy.

### 💼 Agent
* Register and manage their professional profile.
* View all policies and customer details under their management.
* View a detailed personal sales report.
* Automatically calculate their total commission based on sales.
* Update and remove policy packages.

### 👑 Administrator
* Log in to the system-wide admin dashboard.
* Manage agents (view all, remove).
* Approve or reject pending claims filed by customers.
* Validate (approve or reject) custom policies created by customers.
* Generate system-wide sales and agent performance reports.
* Review all policies in the system.

## 💻 Tech Stack

* **Language:** Python
* **Database:** SQLite3
