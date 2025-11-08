from database_setup import sqlite3

def generate_agent_id(db):
    try:
        # Fetch the last agent ID from the database
        db.cursor.execute("SELECT agent_id FROM agents ORDER BY agent_id DESC LIMIT 1")
        result = db.cursor.fetchone()

        if result:
            # Extract the numeric part of the last ID and increment it
            last_id = result[0]  # Example: "AG01"
            last_number = int(last_id[2:])  # Extract numeric part (e.g., 01)
            new_number = last_number + 1
        else:
            # Start with 1 if no IDs exist
            new_number = 1

        # Format new ID with leading zeros (AG01, AG02, etc.)
        return f"AG{new_number:02d}"
    except Exception as e:
        print(f"Error generating agent ID: {e}")
        # Fallback to timestamp-based ID if there's an error
        return f"AG{datetime.now().strftime('%Y%m%d%H%M%S')}"

def manage_agent_profile(db, nric):
    # Allows agents to view and update their profile
    try:
        # Fetch user profile details from the database
        db.cursor.execute('''
            SELECT users.nric, agents.agent_id, users.email, users.name, users.age, users.contact_number, agents.qualification, agents.commission_rate
            FROM agents
            JOIN users ON users.nric = agents.nric
            WHERE users.nric = ? 
        ''', (nric, ))

        agent = db.cursor.fetchone()

        if not agent:
            print("Agent profile not found.")
            return

        print("\nProfile Details")
        print("================================================")
        print(f"NRIC           : {agent[0]}")
        print(f"Agent ID       : {agent[1]}")
        print(f"Email          : {agent[2]}")
        print(f"Name           : {agent[3]}")
        print(f"Age            : {agent[4]}")
        print(f"Contact Number : {agent[5]}")
        print(f"Qualification  : {agent[6]}")
        print(f"Commission Rate: {agent[7]}")
        print("================================================")
        print("[1] Update Profile")
        print("[2] Back to Main Menu")

        choice = input("Choose an option: ")

        if choice == "1":
            update_profile(db, nric)
        elif choice == "2":
            return  # Back to main menu
        else:
            print("Invalid option. Returning to main menu.")

    except sqlite3.Error as e:
        print(f"Error fetching profile: {e}")

def update_profile(db, nric):

    # Allows the agents to update specific fields in their profile
    try:
        print("\n============[ Update Profile ]============")
        print("[1] NRIC\n[2] Agent ID\n[3] Email\n[4] Name")
        print("[5] Age\n[6] Contact Number\n[7] Qualification\n[8] Commission Rate\n[9] Back to Profile")
        choice = input("Choose a field to update (1-6): ")

        field_map = {
            "1": "nric",
            "2": "agent_id",
            "3": "email",
            "4": "name",
            "5": "age",
            "6": "contact_number",
            "7": "qualification",
            "8": "commission rate",
        }

        if choice == "9":
            return  # Back to profile

        if choice not in field_map:
            print("Invalid choice. Returning to profile.")
            return

        field_to_update = field_map[choice]
        new_value = input(f"Enter your new {field_to_update}: ")

        # Update the selected field in the database
        db.cursor.execute(f'''
            UPDATE users SET {field_to_update} = ? WHERE nric = ? AND role = 'Agent'
        ''', (new_value, nric))

        db.conn.commit()
        print(f"{field_to_update.capitalize()} updated successfully.")

    except sqlite3.Error as e:
        print(f"Error updating profile: {e}")

def update_user_profile(db, nric, field, new_value):
    #Update a specific field in the user's profile
    query = f"UPDATE users SET {field} = ? WHERE nric = ?"
    db.cursor.execute(query, (new_value, nric))
    db.conn.commit() 

def manage_policies(db):
    try:
        while True:
            print("\n============[ Manage Policies Menu ]============")
            print("[1] View All Policies")
            print("[2] View Customer Details")
            print("[3] Update Policy Details")
            print("[4] Remove a Policy")
            print("[5] Back to Main Menu")

            choice = input("Choose an option: ")

            if choice == "1":
                view_all_policies(db)
            elif choice == "2":
                agent_id = input("Enter your Agent ID: ")
                nric = input("Enter Customer NRIC to view details: ")
                view_customer_details(db, agent_id, nric)
            elif choice == "3":
                policy_id = input("Enter Policy ID to update: ")
                update_policy_details(db, policy_id)
            elif choice == "4":
                policy_id = input("Enter Policy ID to delete: ")
                delete_policy(db, policy_id)
            elif choice == "5":
                break
            else:
                print("Invalid option. Please try again.")

    except Exception as e:
        print(f"Error managing policies: {e}")

def view_all_policies(db):
    try:
        db.cursor.execute("SELECT * FROM policy_package")
        policies = db.cursor.fetchall()

        # Headers
        custom_headers = ["Policy ID", "Policy Type", "Policy Plan", "Coverage Amount", "Premium", "Custom Data"]

        header = " | ".join(f"{col:<20}" for col in custom_headers)
        print("\n" + "=" * len(header))
        print(header)
        print("=" * len(header))

        # Print each policy row 
        for policy in policies:
    
            policy_id = policy[0]  
            policy_type = policy[1] 
            policy_plan = policy[2]
            coverage_amount = policy[3]
            premium = policy[4]
            custom_data = policy[5]

            # Format and print the row
            row = " | ".join(f"{str(item):<20}" for item in [
                policy_id, policy_type, policy_plan, coverage_amount, premium, custom_data
            ])
            print(row)

        print("=" * len(header))

    except Exception as e:
        print(f"Error fetching policies: {e}")

def view_customer_details(db, agent_id, nric):
    try:
        db.cursor.execute(
            "SELECT * FROM purchased_policy WHERE agent_id = ?", (agent_id,)
        )
        policies = db.cursor.fetchall()

        if not policies:
            print(f"No policies found for Agent ID: {agent_id}")
            return

        # Display list of customers in table
        headers = [desc[0] for desc in db.cursor.description]
        column_widths = [max(len(str(row[i])) for row in [headers] + policies) for i in range(len(headers))]

        # Print header
        print("\nPolicies List")
        print("=" * (sum(column_widths) + len(column_widths) - 1))
        header_row = " | ".join(f"{headers[i]:<{column_widths[i]}}" for i in range(len(headers)))
        print(header_row)
        print("-" * len(header_row))

        # Print each policy row
        for policy in policies:
            row = " | ".join(f"{str(policy[i]):<{column_widths[i]}}" for i in range(len(policy)))
            print(row)

        print("=" * len(header_row))

        # Display individual customer details
        db.cursor.execute('''
            SELECT users.nric, users.name, users.email, users.contact_number 
            FROM users 
            WHERE users.nric = ?
        ''', (nric,))
        customer = db.cursor.fetchone()

        if not customer:
            print("Customer details not found.")
            return
        
        print("\nCustomer Details")
        print("================================================")
        print(f"NRIC           : {customer[0]}")
        print(f"Name           : {customer[1]}")
        print(f"Email          : {customer[2]}")
        print(f"Contact Number : {customer[3]}")

        # Display customer policy details
        db.cursor.execute('''
            SELECT purchased_policy.customer_id, purchased_policy.policy_plan, purchased_policy.premium, purchased_policy.coverage_amount
            FROM purchased_policy
            WHERE purchased_policy.agent_id = ?
        ''', (agent_id,))
        policy = db.cursor.fetchone()

        if not policy:
            print("Policy details not found.")
            return

        print(f"Customer ID    : {policy[0]}")
        print(f"Plan           : {policy[1]}")
        print(f"Premium        : {policy[2]}")
        print(f"Coverage       : {policy[3]}")
        print("================================================")

    except sqlite3.Error as e:
        print(f"Error fetching customer details: {e}")

def update_policy_details(db, policy_id):
    try:
        print("\n============[ Update Policy Details ]============")
        print("[1] Plan\n[2] Premium\n[3] Coverage\n[4] Back to Policies Menu")
        choice = input("Choose a field to update (1-4): ")

        field_map = {
            "1": "plan",
            "2": "premium",
            "3": "coverage",
        }

        if choice == "4":
            return  # Back to policies menu

        if choice not in field_map:
            print("Invalid choice. Returning to policies menu.")
            return

        field_to_update = field_map[choice]
        new_value = input(f"Enter the new {field_to_update}: ")

        # Update the selected field in the database
        db.cursor.execute(f'''
            UPDATE policy_package SET {field_to_update} = ? WHERE policy_id = ?
        ''', (new_value, policy_id))

        db.conn.commit()
        print(f"{field_to_update.capitalize()} updated successfully.")

    except sqlite3.Error as e:
        print(f"Error updating policy details: {e}")

def delete_policy(db, policy_id):
    try:
        confirm = input("Are you sure you want to delete this policy? (yes/no): ")
        if confirm.lower() != "yes":
            print("Policy deletion canceled.")
            return

        db.cursor.execute("DELETE FROM policy_package WHERE policy_id = ?", (policy_id,))
        db.conn.commit()
        print("Policy deleted successfully.")

    except sqlite3.Error as e:
        print(f"Error deleting policy: {e}")

def calculate_commission(db, agent_id):
    try:
        # Fetch the agent's commission rate
        db.cursor.execute('''
            SELECT commission_rate 
            FROM agents 
            WHERE agent_id = ?
        ''', (agent_id,))
        result = db.cursor.fetchone()

        if not result:
            print("Agent not found.")
            return

        commission_rate = result[0]

        # Fetch the total premiums from policies sold by the agent
        db.cursor.execute('''
            SELECT SUM(p.premium) 
            FROM purchased_policy AS pp
            JOIN policy_package AS p ON pp.policy_id = p.policy_id
            WHERE pp.agent_id = ?
        ''', (agent_id,))
        total_premium = db.cursor.fetchone()[0] or 0  # Default to 0 if no policies are sold

        # Calculate total commission
        total_commission = total_premium * (commission_rate / 100)

        # Display the results
        print("\n============[ Commission Details ]============")
        print(f"Total Premium Earned : RM{total_premium:.2f}")
        print(f"Commission Rate      : {commission_rate}%")
        print(f"Total Commission     : RM{total_commission:.2f}")
        print("================================================")

    except sqlite3.Error as e:
        print(f"Error calculating commission: {e}")

def view_sales_report(db, agent_id):
    try:
        # Fetch sales details
        db.cursor.execute('''
            SELECT purchased_policy.policy_id, purchased_policy.customer_id, purchased_policy.policy_type, purchased_policy.premium, purchased_policy.start_date 
            FROM purchased_policy 
            WHERE purchased_policy.agent_id = ?
            ORDER BY start_date DESC;

        ''', (agent_id,))

        sales = db.cursor.fetchall()

        if not sales:
            print("No sales records found for this agent.")
            return

        print("\n======================[ Sales Report ]==========================")
        print("Policy ID | Customer ID | Policy Type | Premium Amount | Sale Date")
        print("-" * 64)

        for sale in sales:
            print(f"{sale[0]}      | {sale[1]}         | {sale[2]}      | {sale[3]}       | {sale[4]}")

    # Retrieve the agent's commission rate
        db.cursor.execute('''
            SELECT commission_rate 
            FROM agents 
            WHERE agent_id = ?;
        ''', (agent_id,))

        commission_rate = db.cursor.fetchone()

        if not commission_rate:
            print("Agent commission rate not found.")
            return

        commission_rate = commission_rate[0]

        # Calculate total policies sold yearly and total commission
        db.cursor.execute('''
            SELECT strftime('%Y', start_date) AS year, COUNT(*) AS total_policies, 
                   SUM(premium * ?) AS total_commission 
            FROM purchased_policy 
            WHERE agent_id = ?
            GROUP BY year
            ORDER BY year DESC;
        ''', (commission_rate, agent_id))

        yearly_summary = db.cursor.fetchall()

        print("\n=============[ Yearly Summary ]=============")
        print("Year | Total Policies Sold | Total Commission")
        print("-" * 44)

        for summary in yearly_summary:
            print(f"{summary[0]} |      {summary[1]}              | {summary[2]:.2f}")
            
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving the sales report: {e}")