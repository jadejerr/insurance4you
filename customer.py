from database_setup import sqlite3
from insurance_class import LifeInsurance, VehicleInsurance, HealthInsurance, PropertyInsurance, PolicyPlan, PolicyType, generate_policy_id

def generate_customer_id(db):
    """
    Generate a new customer ID in the format C01, C02, etc.
    """
    try:
        # Fetch the last customer ID from the database
        db.cursor.execute("SELECT customer_id FROM customers ORDER BY customer_id DESC LIMIT 1")
        result = db.cursor.fetchone()

        if result:
            # Extract the numeric part of the last ID and increment it
            last_id = result[0]  # Example: "C01"
            last_number = int(last_id[1:])  # Extract numeric part (e.g., 01)
            new_number = last_number + 1
        else:
            # Start with 1 if no IDs exist
            new_number = 1

        # Format new ID with leading zeros (C01, C02, etc.)
        return f"C{new_number:02d}"
    except Exception as e:
        print(f"Error generating customer ID: {e}")
        # Fallback to timestamp-based ID if there's an error
        return f"C{datetime.now().strftime('%Y%m%d%H%M%S')}"

def manage_customer_profile(db, nric):
    # Allows the customer to view and update their profile
    try:
        # Fetch user profile details from the database
        db.cursor.execute('''
            SELECT users.nric, customers.customer_id, users.email, users.name, users.age, users.contact_number, customers.occupation, customers.income 
            FROM customers 
            JOIN users ON users.nric = customers.nric 
            WHERE users.nric = ?
        ''', (nric, ))

        customer = db.cursor.fetchone()

        if not customer:
            print("Customer profile not found.")
            return

        print("\nProfile Details")
        print("================================================")
        print(f"NRIC           : {customer[0]}")
        print(f"Customer ID    : {customer[1]}")
        print(f"Email          : {customer[2]}")
        print(f"Name           : {customer[3]}")
        print(f"Age            : {customer[4]}")
        print(f"Contact Number : {customer[5]}")
        print(f"Occupation     : {customer[6]}")
        print(f"Income         : {customer[7]}")
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

    # Allows the customer to update specific fields in their profile
    try:
        print("\n============[ Update Profile ]============")
        print("[1] ID\n[2] Email\n[3] Password\n[4] Name\n[5] Age\n[6] Contact Number\n[7] Back to Profile")
        choice = input("Choose a field to update (1-6): ")

        field_map = {
            "1": "nric",
            "2": "email",
            "3": "password",
            "4": "name",
            "5": "age",
            "6": "contact_number"
        }

        if choice == "7":
            return  # Back to profile

        if choice not in field_map:
            print("Invalid choice. Returning to profile.")
            return

        field_to_update = field_map[choice]
        new_value = input(f"Enter your new {field_to_update}: ")

        # Update the selected field in the database
        db.cursor.execute(f'''
            UPDATE users SET {field_to_update} = ? WHERE nric = ? AND role = 'Customer'
        ''', (new_value, nric))

        db.conn.commit()
        print(f"{field_to_update.capitalize()} updated successfully.")

    except sqlite3.Error as e:
        print(f"Error updating profile: {e}")

def update_user_profile(db, nric, field, new_value):
    # Update a specific field in the user's profile
    query = f"UPDATE users SET {field} = ? WHERE nric = ?"
    db.cursor.execute(query, (new_value, nric))
    db.conn.commit()

def file_claim(db, customer_id):
    # Allows a customer to file an insurance claim for their purchased policies
    print("\n============[ File an Insurance Claim ]============")

    try:
        # Fetch purchased policies for the customer
        db.cursor.execute("""
            SELECT policy_id, policy_type, policy_plan, status
            FROM purchased_policy
            WHERE customer_id = ? AND status IN ('Active', 'Premium paid')
        """, (customer_id,))
        policies = db.cursor.fetchall()

        if not policies:
            print("No eligible policies found for filing a claim.")
            return

        # Display the eligible policies
        print("\nEligible Policies for Filing a Claim:")
        for i, policy in enumerate(policies, 1):
            print(f"\n[{i}] Policy ID: {policy[0]}")
            print(f"   Type: {policy[1]}")
            print(f"   Plan: {policy[2]}")
            print(f"   Status: {policy[3]}")

        # Allow the customer to select a policy
        try:
            policy_choice = int(input("\nSelect a policy to file a claim for (number): ")) - 1
        except ValueError:
            print("Invalid input! Please enter a valid number.")
            return

        if 0 <= policy_choice < len(policies):
            selected_policy = policies[policy_choice]
            policy_id = selected_policy[0]

            # Gather claim details
            details = input("Enter claim details: ")
            amount = float(input("Enter claim amount: RM"))

            # Generate the next claim ID
            db.cursor.execute("SELECT claim_id FROM claims ORDER BY claim_id DESC LIMIT 1")
            last_claim = db.cursor.fetchone()

            if last_claim:
                # Extract the numeric part of the last claim ID and increment it
                last_number = int(last_claim[0][1:])  # Skip the first character (e.g., 'C')
                new_number = last_number + 1
            else:
                # If no claims exist, start with C01
                new_number = 1

            # Format the new claim ID
            claim_id = f"C{new_number:02}"

            # Insert the claim into the database
            db.cursor.execute("""
                INSERT INTO claims (claim_id, policy_id, customer_id, details, amount, status, date_filed)
                VALUES (?, ?, ?, ?, ?, 'Pending request', CURRENT_TIMESTAMP)
            """, (claim_id, policy_id, customer_id, details, amount))

            db.conn.commit()
            print("\nClaim filed successfully!")
            print(f"Claim ID     : {claim_id}")
            print(f"Policy ID    : {policy_id}")
            print(f"Claim Amount : RM{amount:,.2f}")
            print(f"Status       : Pending request")
        else:
            print("Invalid policy selection!")
    except Exception as e:
        print(f"Error filing claim: {e}")
        db.conn.rollback()

def choose_insurance(db, nric):
    # Allow users to choose between prepared policies or custom policies
    while True:
        print("\n============[ Insurance Selection ]============")
        print("[1] View Prepared Insurance Policies")
        print("[2] Create Custom Insurance Policy")
        print("[3] Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            select_prepared_policy(db, nric)
        elif choice == "2":
            create_custom_policy(db, nric)
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

def select_prepared_policy(db, nric):
    # Display and allow selection of prepared insurance policies
    print("\n============[ Available Insurance Policies ]============")
    print("Select Insurance Type:")
    print("[1] Life Insurance")
    print("[2] Vehicle Insurance")
    print("[3] Health Insurance")
    print("[4] Property Insurance")

    type_choice = input("Enter choice: ")
    policy_types = {
        "1": "LIFE",
        "2": "VEHICLE",
        "3": "HEALTH",
        "4": "PROPERTY"
    }

    if type_choice not in policy_types:
        print("Invalid choice!")
        return

    selected_type = policy_types[type_choice]

    # Fetch available policies of selected type
    try:
        db.cursor.execute("""
            SELECT policy_id, policy_plan, coverage_amount, premium, custom_data
            FROM policy_package
            WHERE policy_type = ? AND policy_plan != 'CUSTOM'
        """, (selected_type,))

        policies = db.cursor.fetchall()

        if not policies:
            print("No policies available for this type.")
            return

        print("\nAvailable Plans:")
        for i, policy in enumerate(policies, 1):
            print(f"\n[{i}] {policy[1]} Plan")
            print(f"   Coverage Amount     : RM{policy[2]:,}")
            print(f"   Premium             : RM{policy[3]:,}")
            print(f"   Additional Benefits : {policy[4]}")

        policy_choice = int(input("\nSelect a plan (number): ")) - 1
        if 0 <= policy_choice < len(policies):
            selected_policy = policies[policy_choice]

            # Get an agent
            db.cursor.execute("""
                SELECT agents.nric, users.name 
                FROM agents
                JOIN users ON agents.nric = users.nric
                ORDER BY RANDOM()
                LIMIT 1
            """)
            agent = db.cursor.fetchone()

            if agent:
                agent_nric = agent[0]
                agent_name = agent[1]

                # Insert into purchased_policy
                db.cursor.execute("""
                    INSERT INTO purchased_policy 
                    (customer_id, policy_id, agent_id, policy_type, policy_plan, coverage_amount, premium, status, start_date, end_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATE('now'), DATE('now', '+1 year'))
                """, (nric, selected_policy[0], agent_nric, selected_type, selected_policy[1], selected_policy[2], selected_policy[3], 'Pending request'))

                db.conn.commit()
                print("\nPolicy purchased successfully!")
                print(f"Your Agent: {agent_name}")
            else:
                print("No agents available at the moment.")

    except Exception as e:
        print(f"Error: {e}")
        db.conn.rollback()

def create_custom_policy(db, nric):
    # Allow users to create a custom insurance policy using subclass methods
    print("\n============[ Custom Insurance Policy ]============")
    print("Select Insurance Type:")
    print("[1] Life Insurance")
    print("[2] Vehicle Insurance")
    print("[3] Health Insurance")
    print("[4] Property Insurance")

    type_choice = input("Enter choice: ")

    try:
        # Get basic policy details
        coverage_amount = float(input("Enter desired coverage amount: RM"))

        # Initialize appropriate insurance object based on type
        if type_choice == "1":
            # Get life insurance specific details
            beneficiary = input("Enter beneficiary name: ")
            death_benefit = coverage_amount  # Usually equals coverage amount
            medical_history = input("Enter medical history (None/Conditions): ")
            age = int(input("Enter age: "))  # Usually equals coverage amount

            # Create life insurance instance
            insurance = LifeInsurance(
                policy_plan="CUSTOM",
                coverage_amount=coverage_amount,
                premium=0,  # Will be calculated
                start_date="DATE('now')",
                end_date="DATE('now', '+1 year')",
                status='Pending request',
                beneficiary=beneficiary,
                death_benefit=death_benefit,
                medical_history=medical_history
            )
            # Calculate premium using subclass method
            premium = insurance.calculate_life_premium(age, coverage_amount)
            insurance.premium = premium
            custom_data = f"Beneficiary: {beneficiary}, Medical History: {medical_history}"
            policy_type = PolicyType.LIFE.value

        elif type_choice == "2":
            # Get vehicle insurance specific details
            vehicle_value = float(input("Enter vehicle value: RM"))
            vehicle_age = int(input("Enter vehicle age (years): "))
            vehicle_type = input("Enter vehicle type: ")
            vehicle_registration = input("Enter vehicle registration number: ")

            # Create vehicle insurance instance
            insurance = VehicleInsurance(
                policy_plan="CUSTOM",
                coverage_amount=coverage_amount,
                premium=0,  # Will be calculated
                start_date="DATE('now')",
                end_date="DATE('now', '+1 year')",
                status='Pending request',
                vehicle_details={'type': vehicle_type, 'value': vehicle_value, 'age': vehicle_age},
                accident_coverage=True
            )
            # Calculate premium using subclass method
            premium = insurance.calculate_vehicle_premium(vehicle_value, vehicle_age)
            insurance.premium = premium
            custom_data = f"Vehicle Type: {vehicle_type}, Vehicle Value: RM{vehicle_value}"
            policy_type = PolicyType.VEHICLE.value

        elif type_choice == "3":
            # Initialize Health Insurance variables first
            coverage_type = input("Enter desired coverage type (Basic/Comprehensive): ")
            medical_history = input("Enter medical history (None/Conditions): ")
            deductible = float(input("Enter deductible amount: RM"))
            copayment = float(input("Enter copayment percentage: "))
            age = int(input("Enter age: "))

            # Create health insurance instance
            insurance = HealthInsurance(
                policy_plan="CUSTOM",
                coverage_amount=coverage_amount,
                premium=0,  # Will be calculated
                start_date="DATE('now')",
                end_date="DATE('now', '+1 year')",
                status='Pending request',
                coverage_type=coverage_type,
                deductible=deductible,
                copayment=copayment
            )
            # Calculate premium using subclass method
            premium = insurance.calculate_health_premium(age, medical_history)
            insurance.premium = premium
            custom_data = f"Coverage Type: {coverage_type}, Medical History: {medical_history}"
            policy_type = PolicyType.HEALTH.value

        elif type_choice == "4":
            # Initialize Property Insurance variables first
            property_type = input("Enter property type (residential/commercial/industrial): ")
            property_value = float(input("Enter property value: RM"))
            property_age = int(input("Enter property age (years): "))
            property_address = input("Enter property address: ")

            # Create property insurance instance
            insurance = PropertyInsurance(
                policy_plan="CUSTOM",
                coverage_amount=coverage_amount,
                premium=0,  # Will be calculated
                start_date="DATE('now')",
                end_date="DATE('now', '+1 year')",
                status='Pending request',
                property_address=property_address,
                property_value=property_value,
                property_type=property_type
            )
            # Calculate premium using subclass method
            premium = insurance.calculate_property_premium(property_value, property_age)
            insurance.premium = premium
            custom_data = f"Property Type: {property_type}, Property Value: RM{property_value}"
            policy_type = PolicyType.PROPERTY.value

        else:
            print("Invalid choice!")
            return

        # Get a random agent
        db.cursor.execute("SELECT agent_id FROM agents ORDER BY RANDOM() LIMIT 1")
        agent = db.cursor.fetchone()

        # Get customer id
        db.cursor.execute("SELECT customer_id FROM customers WHERE nric = ?", (nric,))
        customer = db.cursor.fetchone()

        if not customer:
            print("Error: Customer ID not found for the provided NRIC.")
            return

        customer_id = customer[0]

        # Generate policy ID
        policy_id = generate_policy_id(db, policy_type)
        insurance.policy_id = policy_id

        # Insert into policy_package
        db.cursor.execute("""
            INSERT INTO policy_package 
            (policy_id, policy_type, policy_plan, coverage_amount, premium, custom_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (policy_id, policy_type, "CUSTOM", coverage_amount, premium, custom_data))

        # Insert into custom_policy
        db.cursor.execute("""
            INSERT INTO custom_policy 
            (customer_id, policy_id, agent_id, policy_type, policy_plan, 
            coverage_amount, premium, status, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, DATE('now'), DATE('now', '+1 year'))
        """, (customer_id, policy_id, agent[0], policy_type, "CUSTOM",
              coverage_amount, premium, 'Pending request'))

        # Insert into type-specific tables based on policy type
        if type_choice == "1":  # Life Insurance
            db.cursor.execute("""
                INSERT INTO life_policy_details
                (policy_id, beneficiary_name, death_benefit, medical_history)
                VALUES (?, ?, ?, ?)
            """, (policy_id, beneficiary, death_benefit, medical_history))

        elif type_choice == "2":  # Vehicle Insurance
            db.cursor.execute("""
                INSERT INTO vehicle_policy_details
                (policy_id, vehicle_type, vehicle_value, vehicle_age, 
                vehicle_registration, accident_coverage)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (policy_id, vehicle_type, vehicle_value, vehicle_age,
                  vehicle_registration, True))

        elif type_choice == "3":  # Health Insurance
            db.cursor.execute("""
                INSERT INTO health_policy_details
                (policy_id, coverage_type, medical_history, deductible, copayment)
                VALUES (?, ?, ?, ?, ?)
            """, (policy_id, coverage_type, medical_history, deductible, copayment))

        elif type_choice == "4":  # Property Insurance
            db.cursor.execute("""
                INSERT INTO property_policy_details
                (policy_id, property_address, property_type, property_value, property_age)
                VALUES (?, ?, ?, ?, ?)
            """, (policy_id, property_address, property_type, property_value, property_age))

        db.conn.commit()
        print(f"\nCustom policy created successfully!")
        print(f"Premium calculated: RM{premium:,.2f}")
        print("Status: Pending request (Waiting for validation)")

    except Exception as e:
        print(f"Error: {e}")
        db.conn.rollback()

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

            if choice == "1" or choice == "2":
                status = "Accepted" if choice == "1" else "Rejected"

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

def view_status(db, nric):
    # Allow customer to view their policies status
    print("\n============[ Purchased Policies Status ]============")

    try:
        # Fetch purchased policies for the given customer with agent details
        db.cursor.execute("""
            SELECT pp.policy_id, pp.policy_type, pp.policy_plan, pp.coverage_amount, 
                   pp.premium, pp.status, pp.start_date, pp.end_date, u.name AS agent_name
            FROM purchased_policy pp
            LEFT JOIN agents a ON pp.agent_id = a.agent_id
            LEFT JOIN users u ON a.nric = u.nric
            WHERE pp.customer_id = ?
        """, (nric,))
        policies = db.cursor.fetchall()

        if not policies:
            print("No purchased policies found.")
            return

        # Display policies
        for i, policy in enumerate(policies, 1):
            print(f"\nPolicy #{i}")
            print(f"   Policy ID: {policy[0]}")
            print(f"   Type: {policy[1]}")
            print(f"   Plan: {policy[2]}")
            print(f"   Coverage Amount: RM{policy[3]:,}")
            print(f"   Premium: RM{policy[4]:,}")
            print(f"   Status: {policy[5]}")
            print(f"   Start Date: {policy[6]}")
            print(f"   End Date: {policy[7]}")
            print(f"   Agent: {policy[8] if policy[8] else 'Not Assigned'}")

        print("\n====================================================")
    except Exception as e:
        print(f"Error retrieving policies: {e}")

def make_payment(db, nric):
    # Allow customers to pay premium
    print("\n============[ Pay Premium ]============")

    try:
        # Fetch policies eligible for payment
        db.cursor.execute("""
            SELECT pp.policy_id, pp.policy_type, pp.policy_plan, pp.premium, pp.status
            FROM purchased_policy pp
            LEFT JOIN payments p ON pp.policy_id = p.policy_id AND p.status = 'Completed'
            WHERE pp.customer_id = ? AND pp.status = 'Accepted' AND p.policy_id IS NULL
        """, (nric,))
        policies = db.cursor.fetchall()

        if not policies:
            print("No confirmed policies available for payment.")
            return

        print("\nEligible Policies for Payment:")
        for i, policy in enumerate(policies, 1):
            print(f"\n[{i}] Policy ID: {policy[0]}")
            print(f"   Type: {policy[1]}")
            print(f"   Plan: {policy[2]}")
            print(f"   Premium Amount: ${policy[3]:,}")

        try:
            policy_choice = int(input("\nSelect a policy to pay for (number): ")) - 1
        except ValueError:
            print("Invalid input! Please enter a valid number.")
            return

        if 0 <= policy_choice < len(policies):
            selected_policy = policies[policy_choice]
            policy_id = selected_policy[0]
            premium_amount = selected_policy[3]

            print("\nSelect Payment Option:")
            print("[1] Debit/Credit Card")
            print("[2] Online Banking")
            payment_option = input("Enter choice: ")

            if payment_option not in ['1', '2']:
                print("Invalid payment option!")
                return

            payment_method = "Debit/Credit Card" if payment_option == '1' else "Online Banking"
            payment_id = generate_payment_id(db)

            db.cursor.execute("""
                INSERT INTO payments (payment_id, customer_id, policy_id, amount, 
                                      payment_date, payment_method, status)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, 'Completed')
            """, (payment_id, nric, policy_id, premium_amount, payment_method))

            db.cursor.execute("""
                UPDATE purchased_policy
                SET status = 'Premium paid'
                WHERE policy_id = ? AND customer_id = ?
            """, (policy_id, nric))

            db.conn.commit()

            print("\nPayment successful!")
            print(f"Payment ID: {payment_id}")
            print(f"Policy ID: {policy_id}")
            print(f"Amount Paid: ${premium_amount:,}")
            print(f"Payment Method: {payment_method}")
        else:
            print("Invalid policy selection!")
    except Exception as e:
        print(f"Error during payment process: {e}")
        db.conn.rollback()

def generate_payment_id(db):
    # Generate a new payment ID
    db.cursor.execute("SELECT payment_id FROM payments ORDER BY payment_id DESC LIMIT 1")
    result = db.cursor.fetchone()

    if result and result[0].startswith("PAYMENT"):
        # Extract the numeric part, increment it, and format it back
        last_id = int(result[0][7:])  # Extract numeric part after 'PAYMENT'
        new_id = f"PAYMENT{last_id + 1:03}"
    else:
        # Start with PAYMENT001 if no existing IDs
        new_id = "PAYMENT001"

    return new_id

def cancel_policy(db, customer_id):
    """
    Allows the customer to cancel a specific policy by changing its status to 'Cancelled'.
    """
    print("\n============[ Cancel a Policy ]============")
    try:
        # Fetch active or pending policies for the customer
        db.cursor.execute("""
            SELECT policy_id, policy_type, policy_plan, status
            FROM purchased_policy
            WHERE customer_id = ? AND status NOT IN ('Cancelled', 'Expired')
        """, (customer_id,))
        policies = db.cursor.fetchall()

        if not policies:
            print("No active or pending policies available for cancellation.")
            return

        # Display the eligible policies
        print("\nEligible Policies for Cancellation:")
        for i, policy in enumerate(policies, 1):
            print(f"\n[{i}] Policy ID: {policy[0]}")
            print(f"   Type: {policy[1]}")
            print(f"   Plan: {policy[2]}")
            print(f"   Status: {policy[3]}")

        # Allow the customer to select a policy to cancel
        try:
            policy_choice = int(input("\nSelect a policy to cancel (number): ")) - 1
        except ValueError:
            print("Invalid input! Please enter a valid number.")
            return

        if 0 <= policy_choice < len(policies):
            selected_policy = policies[policy_choice]
            policy_id = selected_policy[0]

            # Update the policy status to 'Cancelled'
            db.cursor.execute("""
                UPDATE purchased_policy
                SET status = 'Cancelled'
                WHERE policy_id = ? AND customer_id = ?
            """, (policy_id, customer_id))
            db.conn.commit()

            print(f"\nPolicy {policy_id} has been successfully cancelled.")
        else:
            print("Invalid policy selection!")
    except Exception as e:
        print(f"Error cancelling policy: {e}")
        db.conn.rollback()