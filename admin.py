import sqlite3
from database_setup import DatabaseManager

def manage_agents(db ,nric):
    print("\nManaging Agents")
    while True:
        print("\n[1] View All Agents")
        print("[2] Remove an Agent")
        print("[3] Back to Main Menu")
        choice = input("Enter your choice: ")

        if choice == "1":
            try:
                db.cursor.execute('''
                    SELECT a.agent_id, a.nric, u.name, a.qualification, a.status
                    FROM agents a
                    JOIN users u ON a.nric = u.nric
                ''')
                agents = db.cursor.fetchall()
                if agents:
                    print("\nAll Agents:")
                    for agent in agents:
                        print(f"ID: {agent[0]}, NRIC: {agent[1]}, Name: {agent[2]}, Qualification: {agent[3]}, Status: {agent[4]}")
                else:
                    print("No agents found.")
            except sqlite3.Error as e:
                print(f"Error retrieving agents: {e}")
        elif choice == "2":
            nric = input("Enter the Agent NRIC to remove: ")
            try:
                db.cursor.execute('SELECT nric FROM agents WHERE nric = ?', (nric,))
                agent = db.cursor.fetchone()

                if agent:
                    db.cursor.execute('DELETE FROM agents WHERE nric = ?', (nric,))
                    db.conn.commit()
                    print(f"Agent {nric} removed successfully.")
                else:
                    print(f"Invalid NRIC: {nric}. No matching agent found.")
            except sqlite3.Error as e:
                print(f"Error removing agent: {e}")
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

def generate_reports(db):
    try:
        db.cursor.execute('''
            SELECT u.name, a.qualification, a.status, a.commission_rate, 
                   SUM(p.premium) AS total_sales
            FROM agents a
            JOIN users u ON a.nric = u.nric
            JOIN purchased_policy p ON a.agent_id = p.agent_id
            GROUP BY a.agent_id
        ''')
        reports = db.cursor.fetchall()
        if reports:
            print("\nReports:\n")
            print(
                f"{'Agent Name':<20} {'Qualification':<15} {'Status':<10} {'Commission Rate (%)':<20} {'Total Sales (RM)':<15}")
            print("-" * 80)

            for report in reports:
                print(f"{report[0]:<20} {report[1]:<15} {report[2]:<10} {report[3]:<20} {report[4]:<15.2f}")
                print("-" * 80)
        else:
            print("No reports available.")
    except sqlite3.Error as e:
        print(f"Error retrieving reports: {e}")

def process_claims_approval(db):
    print("\nProcessing Claims Approval...")

    # Check if the claims table exists and is empty
    try:
        table_name = "claims"
        query = f"SELECT COUNT(*) FROM {table_name}"
        db.cursor.execute(query)
        result = db.cursor.fetchone()[0]

        if result == 0:
            print(f"The table {table_name} is empty.")
            return
        else:
            print(f"The table {table_name} has {result} rows.")

        # Proceed with claims approval if the table is not empty
        db.cursor.execute('''
            SELECT claim_id, policy_id, customer_id, details, amount, status, date_filed
            FROM claims
            WHERE LOWER(status) = "Pending request"
        ''')
        claims = db.cursor.fetchall()

        if claims:
            for claim in claims:
                claim_id, policy_id, customer_id, details, amount, status, date_filed = claim
                print(f"""
                Claim ID: {claim_id}
                Policy ID: {policy_id}
                Customer ID: {customer_id}
                Details: {details}
                Amount: RM {amount:.2f}
                Status: {status}
                Date Filed: {date_filed}
                """)

                # Prompt the user to approve or reject the claim
                decision = input("Approve (a) / Reject (r)? ").lower()
                while decision not in ['a', 'r']:  # Validate input
                    print("Invalid input. Please enter 'a' for approve or 'r' for reject.")
                    decision = input("Approve (a) / Reject (r)? ").lower()

                if decision == 'a':
                    db.cursor.execute('''
                        UPDATE claims
                        SET status = "Accepted"
                        WHERE claim_id = ?
                    ''', (claim_id,))
                    print(f"Claim {claim_id} has been approved.")
                elif decision == 'r':
                    rejection_reason = input("Enter the reason for rejection: ")
                    db.cursor.execute('''
                        UPDATE claims
                        SET status = "Rejected", details = ?
                        WHERE claim_id = ?
                    ''', (f"{details} | Rejection Reason: {rejection_reason}", claim_id))
                    print(f"Claim {claim_id} has been rejected.")

            # Commit the transaction after all claims are processed
            db.conn.commit()
        else:
            print("No pending claims to process.")

    except sqlite3.Error as e:
        print(f"Error processing claims: {e}")

def review_policies(db):
    print("\nReviewing All Policies ")
    try:
        db.cursor.execute('''
            SELECT policy_id, policy_type, policy_plan, coverage_amount, premium 
            FROM policy_package
        ''')
        policies = db.cursor.fetchall()
        if policies:
            print("\nPolicies:")
            for policy in policies:
                print(f"Policy ID: {policy[0]}, Type: {policy[1]}, Plan: {policy[2]}, "
                      f"Coverage Amount: {policy[3]}, Premium: {policy[4]}")
        else:
            print("No policies found.")
    except sqlite3.Error as e:
        print(f"Error reviewing policies: {e}")

def validate_custom_policy(db):
    """
    Function to validate pending custom policies by admin.
    Fetches all pending custom policies and allows admin to approve or reject them.
    Updates the policy status in the database accordingly.
    """
    try:
        # Fetch all pending custom policies
        db.cursor.execute('''
            SELECT 
                cp.customer_id,
                cp.policy_id,
                cp.agent_id,
                cp.policy_type,
                cp.coverage_amount,
                cp.premium,
                u.name as customer_name,
                pp.custom_data
            FROM custom_policy cp
            JOIN users u ON cp.customer_id = u.nric
            JOIN policy_package pp ON cp.policy_id = pp.policy_id
            WHERE cp.status = 'Pending request'
        ''')

        pending_policies = db.cursor.fetchall()

        if not pending_policies:
            print("\nNo pending custom policies to validate.")
            return

        print("\n============[ Pending Custom Policies ]============")
        for policy in pending_policies:
            print(f"\nPolicy ID        : {policy[1]}")
            print(f"Customer ID        : {policy[6]} (ID: {policy[0]})")
            print(f"Agent ID           : {policy[2]}")
            print(f"Policy Type        : {policy[3]}")
            print(f"Coverage Amount    : ${policy[4]:,.2f}")
            print(f"Premium            : ${policy[5]:,.2f}")
            print(f"Additional Details : {policy[7]}")
            print("===================================================")
            print("[1] Approve")
            print("[2] Reject")
            print("[3] Skip to next")

            choice = input("Enter your choice: ")

            if choice == "1":
                status = "Accepted"
            elif choice == "2":
                status = "Rejected"

                # Update status in custom_policy table
                db.cursor.execute('''
                    UPDATE custom_policy 
                    SET status = ? 
                    WHERE policy_id = ?
                ''', (status, policy[1]))

                # If approved, also insert into purchased_policy table
                if status == "Accepted":
                    db.cursor.execute('''
                        INSERT INTO purchased_policy 
                        (customer_id, policy_id, agent_id, policy_type, policy_plan, 
                        coverage_amount, premium, status, start_date, end_date)
                        SELECT 
                            customer_id, policy_id, agent_id, policy_type, policy_plan,
                            coverage_amount, premium, ?, DATE('now'), DATE('now', '+1 year')
                        FROM custom_policy
                        WHERE policy_id = ?
                    ''', (status, policy[1]))

                db.conn.commit()
                print(f"\nPolicy {policy[1]} has been approved.")

            elif choice == "3":
                continue
            else:
                print("Invalid choice. Skipping to next policy.")
                continue

    except Exception as e:
        print(f"Error validating custom policies: {e}")
        db.conn.rollback()