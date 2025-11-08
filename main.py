from datetime import date
from enum import Enum
from database_setup import sqlite3, DatabaseManager
from customer import manage_customer_profile, file_claim, generate_customer_id, choose_insurance, validate_custom_policy,\
    view_status, make_payment, generate_payment_id, cancel_policy
from insurance_class import PolicyPlan, PolicyType, generate_policy_id, Insurance, LifeInsurance, VehicleInsurance, PropertyInsurance, HealthInsurance
from admin import manage_agents, generate_reports, process_claims_approval, review_policies, validate_custom_policy
from agent import manage_agent_profile, manage_policies, calculate_commission, view_sales_report, generate_agent_id

class PaymentMethod(Enum):
    DEBIT_CREDIT_CARD = "DEBIT_CREDIT_CARD"
    ONLINE_BANKING = "ONLINE_BANKING"

# Register user function
def register_user(db):
    print("\nRegister as: ")
    print("[1] Customer")
    print("[2] Agent")
    choice = input("Enter choice: ")

    if choice not in ['1', '2']:
        print("Invalid choice. Please enter [1] for Customer [2] for Agent.")
        return

    # Common user details
    name = input("Enter name: ")
    nric = input("Enter IC Number: ")
    age = int(input("Enter age: "))
    email = input("Enter email: ")
    contact_number = input("Enter contact number: ")
    password = input("Enter password: ")

    try:
        # Insert user details into the `users` table
        db.cursor.execute('''
            INSERT INTO users (nric, role, name, email, password, contact_number, age)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nric, 'Customer' if choice == '1' else 'Agent', name, email, password, contact_number, age))

        if choice == '1':  # Customer registration
            occupation = input("Enter your occupation: ")
            income = float(input("Enter your income: "))
            customer_id = generate_customer_id(db)

            db.cursor.execute('''
                INSERT INTO customers (customer_id, nric, occupation, income)
                VALUES (?, ?, ?, ?)
            ''', (customer_id, nric, occupation, income))

            print(f"Customer registered successfully with ID: {customer_id}")

        elif choice == '2':  # Agent registration
            qualification = input("Enter your qualification: ")
            commission_rate = float(input("Enter your commission rate: "))
            agent_id = generate_agent_id(db)

            db.cursor.execute('''
                INSERT INTO agents (agent_id, nric, qualification, commission_rate)
                VALUES (?, ?, ?, ?)
            ''', (agent_id, nric, qualification, commission_rate))

            print(f"Agent registered successfully with ID: {agent_id}")

        db.conn.commit()
        print("Registration successful!\n")

    except sqlite3.Error as e:
        print(f"Error during registration: {e}")
        db.conn.rollback()

def login_user(db):
    print("\nLog in as: \n[1] Customer \n[2] Agent \n[3] Administrator")
    user_type_choice = input("Enter choice: ")

    # Get user role based on input (1: customer, 2: agent, 3: admin)
    roles = {"1": "Customer", "2": "Agent", "3": "Administrator"}
    role = roles.get(user_type_choice)

    if role:
        nric = input("Enter your ID: ")
        password = input("Enter your password: ")

        db.cursor.execute('''
            SELECT nric, name
            FROM users
            WHERE nric = ? AND password = ? AND role = ?
        ''', (nric, password, role))

        user = db.cursor.fetchone()

        if user:
            print(f"Login successful! (Welcome, {role.upper()})")
            return nric  # Return the nric for further actions
        else:
            print("Invalid credentials. Please try again.")
            return None
    else:
        print("Invalid choice. Please try again.")
        return None

# Get user role
def get_user_role(db, nric):
    """Fetch the role of the user based on their nric."""
    db.cursor.execute('''
        SELECT role
        FROM users
        WHERE nric = ?
    ''', (nric,))

    row = db.cursor.fetchone()
    if row:
        return row[0]  # return the role (first column of the result)
    else:
        print("User role not found.")
        return None

# ===================================================== Menu Interface =====================================================
# Customer menu
def customer_menu(db, nric):
    while True:
        print("\n============[ Main Menu ]============")
        print("[1] Manage Profile")
        print("[2] Choose Insurance")
        print("[3] View Status")
        print("[4] Pay Premium")
        print("[5] File a Claim")
        print("[6] Cancel Policy")
        print("[7] Log Out")
        choice = input("Enter your choice: ")

        if choice == "1":
            Customer.manage_customer_profile(db, nric)
        elif choice == "2":
            Customer.choose_insurance(db, nric)
        elif choice == "3":
            Customer.view_policy_status(db, nric)
        elif choice == "4":
            Customer.make_payment(db, nric)
        elif choice == "5":
            Customer.file_claim(db, nric)
        elif choice == "6":
            Customer.cancel_policy(db, nric)
        elif choice == "7":
            User.logout()
            break
        else:
            print("Invalid choice.")

# Agent menu
def agent_menu(db, nric):
    while True:
        print("\n============[ Main Menu ]============")
        print("[1] Manage Profile")
        print("[2] Manage Policies")
        print("[3] View Commision")
        print("[4] Sales Report")
        print("[5] Log Out")
        choice = input("Enter your choice: ")

        if choice == "1":
            Agent.manage_agent_profile(db, nric)
        elif choice == "2":
            Agent.manage_policies(db)
        elif choice == "3":
            agent_id = input("Enter your Agent ID: ")
            Agent.calculate_commission(db, agent_id)
        elif choice == "4":
            agent_id = input("Enter your Agent ID: ")
            Agent.view_sales_report(db, agent_id)
        elif choice == "5":
            print("Logging out...")
            break
        else:
            print("Feature not implemented yet. Please choose another option.")

# Admin menu
def admin_menu(db, nric):
    while True:
        print("\n============[ Administrator Menu ]============")
        print("[1] Manage Agents")
        print("[2] Generate Reports")
        print("[3] Process Claims Approval")
        print("[4] Review Policies")
        print("[5] Validate Custom Policy")
        print("[6] Log Out")
        choice = input("Enter your choice: ")

        if choice == "1":
            Administrator.manage_agents(db, nric)
        elif choice == "2":
            Administrator.generate_reports(db)
        elif choice == "3":
            Administrator.process_claims_approval(db)
        elif choice == "4":
            Administrator.review_policies(db)
        elif choice == "5":
            Administrator.validate_custom_policy(db)
        elif choice == "6":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")

# ===================================================== Base User Class =====================================================
class User:
    def __init__(self, nric, name, email, contact_number, age, password):
        self.nric = nric
        self.name = name
        self.email = email
        self.contact_number = contact_number
        self.age = age
        self.password = password

    def register(db):
        register_user(db)

    def login(db):
        # Login user
        nric = login_user(db)
        # After login, check user role to determine what menu to show
        if nric:
            role = get_user_role(db, nric)
            if role == 'Customer':
                customer_menu(db, nric)
            elif role == 'Agent':
                agent_menu(db, nric)
            elif role == 'Administrator':
                admin_menu(db, nric)
            else:
                print(f"Role '{role}' functionality is not yet implemented.")

    def logout():
        print("Logging out...")

# Customer Subclass
class Customer(User):
    def __init__(self, nric, customer_id, name, email, contact_number, age, password, occupation, income):
        super().__init__(nric, name, email, contact_number, age, password)
        self.customer_id = customer_id
        self.occupation = occupation
        self.income = income

    def manage_customer_profile(db, nric):
        manage_customer_profile(db, nric)

    def choose_insurance(db, nric):
        choose_insurance(db, nric)

    def view_policy_status(db, nric):
        view_status(db, nric)

    def make_payment(db, nric):
        make_payment(db, nric)

    def file_claim(db, customer_id):
        file_claim(db, customer_id)

    def cancel_policy(db, nric):
        cancel_policy(db, nric)

# Agent Subclass
class Agent(User):
    def __init__(self, nric, name, email, contact_number, age, password, agent_id, commission, qualification):
        super().__init__(nric, name, email, contact_number, age, password)
        self.agent_id = agent_id
        self.commission = commission
        self.qualification = qualification

    def manage_agent_profile(db, nric):
        manage_agent_profile(db, nric)

    def manage_policies(db):
        manage_policies(db)

    def calculate_commission(db, agent_id):
        calculate_commission(db, agent_id)

    def view_sales_report(db, agent_id):
        view_sales_report(db, agent_id)

# Administrator Subclass
class Administrator(User):
    def __init__(self, nric, name, email, contact_number, age, password, admin_id):
        super().__init__(nric, name, email, contact_number, age, password)
        self.admin_id = admin_id

    def manage_agents(db, nric):
        manage_agents(db, nric)

    def generate_reports(db):
        generate_reports(db)

    def process_claims_approval(db):
        process_claims_approval(db)

    def review_policies(db):
        review_policies(db)

    def validate_custom_policy(db):
        validate_custom_policy(db)

# Connect to Database
db = DatabaseManager()
db.connect()

while True:
    # Welcome page
    print("\n===============[ Welcome To Insurance4You ]===============")
    print("[1] Register \n[2] Login \n[3] Exit")
    choice = input("Enter choice: ")
    try:
        if choice == '1': # Register user
            User.register(db)
        elif choice == '2': # Login user
            User.login(db)
        elif choice == '3':
            print("Thank you for using Insurance4You. Goodbye!")
            db.close()
            break
        else:
            print("Invalid choice. Please try again.")
    except Exception as e:
        print(f"An error occurred: {e}")

        # Optional: Ask if user wants to continue
        continue_choice = input("\nWould you like to return to main menu? (y/n): ")
        if continue_choice.lower() != 'y':
            print("Thank you for using Insurance4You. Goodbye!")
            db.close()
            break