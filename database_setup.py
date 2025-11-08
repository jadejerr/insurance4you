import sqlite3

class DatabaseManager:
    def __init__(self, db_name="insurance_system.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        # Establish database connection
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Successfully connected to {self.db_name}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def close(self):
        # Close database connection
        if self.conn:
            self.conn.close()
            print("Database connection closed")

    def init_database(self):
        # Initialize database tables
        try:
            # Users table (base table for all user types)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    nric TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    contact_number TEXT,
                    age INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Additional customer details
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id VARCHAR(5) PRIMARY KEY,
                    nric TEXT,
                    occupation TEXT,
                    income DECIMAL(10,2),
                    FOREIGN KEY (nric) REFERENCES users (nric)
                )
            ''')

            # Additional agent details
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    nric TEXT,
                    qualification TEXT,
                    commission_rate DECIMAL(5,2),
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (nric) REFERENCES users (nric)
                )
            ''')

            # Policy package table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS policy_package (
                    policy_id TEXT PRIMARY KEY,
                    policy_type TEXT,
                    policy_plan TEXT,
                    coverage_amount INTEGER,
                    premium INTEGER,
                    custom_data TEXT
                )
            ''')

            # Purchased policy (relationship table)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchased_policy (
                    customer_id TEXT,
                    policy_id TEXT,
                    agent_id TEXT,
                    policy_type TEXT,
                    policy_plan TEXT,
                    coverage_amount INTEGER,
                    premium INTEGER,
                    status TEXT DEFAULT 'active',
                    start_date DATE,
                    end_date DATE,
                    PRIMARY KEY (customer_id, policy_id),
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
                    FOREIGN KEY (policy_id) REFERENCES policy_package (policy_id),
                    FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
                )
            ''')

            # Custom policy (relationship table)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_policy (
                    customer_id TEXT,
                    policy_id TEXT,
                    agent_id TEXT,
                    policy_type TEXT,
                    policy_plan TEXT DEFAULT 'CUSTOM',
                    coverage_amount INTEGER,
                    premium INTEGER,
                    status TEXT,
                    start_date DATE,
                    end_date DATE,
                    PRIMARY KEY (customer_id, policy_id),
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
                    FOREIGN KEY (policy_id) REFERENCES policy_package (policy_id),
                    FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
                )
            ''')

            # Life Insurance Details table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS life_policy_details (
                    policy_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    beneficiary_name TEXT,
                    death_benefit DECIMAL(12,2),
                    medical_history TEXT,
                    FOREIGN KEY (policy_id) REFERENCES policy_package (policy_id),
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            ''')

            # Vehicle Insurance Details table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicle_policy_details (
                    policy_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    vehicle_type TEXT,
                    vehicle_value DECIMAL(12,2),
                    vehicle_age INTEGER,
                    vehicle_registration TEXT,
                    accident_coverage BOOLEAN,
                    FOREIGN KEY (policy_id) REFERENCES policy_package (policy_id),
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            ''')

            # Property Insurance Details table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS property_policy_details (
                    policy_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    property_address TEXT,
                    property_type TEXT,
                    property_value DECIMAL(12,2),
                    property_age INTEGER,
                    FOREIGN KEY (policy_id) REFERENCES policy_package (policy_id),
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            ''')

            # Health Insurance Details table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_policy_details (
                    policy_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    coverage_type TEXT,
                    medical_history TEXT,
                    deductible DECIMAL(10,2),
                    copayment DECIMAL(5,2),
                    FOREIGN KEY (policy_id) REFERENCES policy_package (policy_id),
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            ''')

            # Claims table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS claims (
                    claim_id TEXT PRIMARY KEY,
                    policy_id TEXT,
                    customer_id TEXT,
                    details TEXT,
                    amount DECIMAL(12,2),
                    status TEXT DEFAULT 'pending',
                    date_filed DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processed_date DATETIME,
                    FOREIGN KEY (policy_id) REFERENCES policies (policy_id),
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                )
            ''')

            # Payments table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    policy_id TEXT,
                    amount DECIMAL(10,2),
                    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    payment_method TEXT,
                    status TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
                    FOREIGN KEY (policy_id) REFERENCES policies (policy_id)
                )
            ''')

            self.conn.commit()
            print("Database tables created successfully")

        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            raise

    def add_test_data(self):
        # Add some test data to the database
        try:
            # Add test users
            test_data = [
                # Customers
                ("970521125566", "Customer", "Jake Evans", "jakeevans@gmail.com", "jake123", "0107193208", 28),
                ("010410150097", "Customer", "Yvette Lee", "yvlee@gmail.com", "yvlee321", "0163489989", 24),
                ("850317138494", "Customer", "Muhamad Haikal", "haikal@gmail.com", "haikal000", "0102905366", 40),
                # Agents
                ("041210150087", "Agent", "Nadya Sofea", "nsofea@gmail.com", "nsofea123", "0178472398", 21),
                ("030501125466", "Agent", "Clementine Josh", "clement@gmail.com", "clement000", "0108813437", 22),
                ("001010145570", "Agent", "Jeff Bernat", "jeff@gmail.com", "jeff404", "0149784421", 25),
                # Administrator
                ("950730134677", "Administrator", "Grace Talentino", "grace@gmail.com", "admingrace", "0162296280", 30),
                ("920122114450", "Administrator", "Syafiq Iman", "syfqimn@gmail.com", "adminsyafiq", "0101219055", 33)
            ]

            self.cursor.executemany('''
                INSERT OR IGNORE INTO users (nric, role, name, email, password, contact_number, age)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', test_data)

            # Add test customer details
            self.cursor.execute('''
                INSERT OR IGNORE INTO customers (nric, customer_id, occupation, income)
                VALUES ('970521125566', 'C01', 'Sales Assistant', 75000.00),
                ('010410150097', 'C02', 'Fashion Designer', 90000.00),
                ('850317138494', 'C03', 'Chief Executive Officer', 250000.00)
            ''')

            # Add test agent details
            self.cursor.execute('''
                INSERT OR IGNORE INTO agents (nric, agent_id, qualification, commission_rate)
                VALUES ('041210150087', 'AG01', 'Master in Finance', 15.00),
                ('030501125466', 'AG02', 'Bachelor in Marketing', 10.00),
                ('001010145570', 'AG03', 'Bachelor in Finance', 12.00)
            ''')

            # Add vehicle policy
            self.cursor.execute('''
                INSERT OR IGNORE INTO policy_package (policy_id, policy_type, policy_plan, coverage_amount, premium, 
                custom_data)
                VALUES 
                ("V001", "VEHICLE", "Standard", 50000, 1200, 
                "Includes roadside assistance and towing service up to 100 miles."),

                ("H001", "HEALTH", "Standard", 20000, 1500, "Includes regular medical check up."),

                ("L001", "LIFE", "Standard", 30000, 100, "Include advisor form lawyers."),

                ("P001", "PROPERTY", "Standard", 20000, 2000, "Include food support when disaster happen."),

                ("V002", "VEHICLE", "Premium", 500000, 15000,"Includes roadside assistance and towing service up to 100 miles."),

                ("H002", "HEALTH", "Premium", 200000, 25000, "Includes regular medical check up."),

                ("L002", "LIFE", "Premium", 300000, 15000, "Include advisor from lawyers."),

                ("P002", "PROPERTY", "Premium", 200000, 20000, "Include food support when disaster happen.")
            ''')

            # Add test purchased policy details
            self.cursor.execute('''
                INSERT OR IGNORE INTO purchased_policy (
                    customer_id, policy_id, agent_id, policy_type, policy_plan, 
                    coverage_amount, premium, status, start_date, end_date
                )
                VALUES 
                    -- Life Insurance policies
                    ('970521125566', 'L001', 'AG01', 'LIFE', 'Standard', 30000, 100, 'Pending request', '2024-01-01', '2025-01-01'),
                    ('010410150097', 'L002', 'AG02', 'LIFE', 'Premium', 300000, 15000, 'Accepted', '2024-02-15', '2025-02-15'),

                    -- Vehicle Insurance policies
                    ('850317138494', 'V001', 'AG01', 'VEHICLE', 'Standard', 50000, 1200, 'Pending request', '2024-03-10', '2025-03-10'),
                    ('970521125566', 'V002', 'AG02', 'VEHICLE', 'Premium', 500000, 15000, 'Accepted', '2024-04-20', '2025-04-20'),

                    -- Health Insurance policies
                    ('010410150097', 'H001', 'AG01', 'HEALTH', 'Standard', 20000, 1500, 'Accepted', '2024-05-05', '2025-05-05'),
                    ('850317138494', 'H002', 'AG02', 'HEALTH', 'Premium', 200000, 25000, 'Accepted', '2024-06-15', '2025-06-15'),

                    -- Property Insurance policies
                    ('970521125566', 'P001', 'AG01', 'PROPERTY', 'Standard', 20000, 2000, 'Pending request', '2024-07-01', '2025-07-01'),
                    ('010410150097', 'P002', 'AG02', 'PROPERTY', 'Premium', 200000, 20000, 'Pending request', '2024-08-10', '2025-08-10'),

                    -- Some policies with different statuses
                    ('850317138494', 'L001', 'AG01', 'LIFE', 'Standard', 30000, 100, 'Cancelled', '2024-01-01', '2025-01-01'),
                    ('970521125566', 'H001', 'AG02', 'HEALTH', 'Standard', 20000, 1500, 'Expired', '2023-05-05', '2024-05-05')
            ''')

            # Add test custom policy packages
            self.cursor.execute('''
                INSERT OR IGNORE INTO policy_package (
                    policy_id, policy_type, policy_plan, coverage_amount, premium, custom_data
                )
                VALUES 
                    ('L003', 'LIFE', 'CUSTOM', 450000, 20000, 'Beneficiary: Sarah Lee, Medical History: None'),
                    ('V003', 'VEHICLE', 'CUSTOM', 75000, 2500, 'Vehicle Type: Tesla Model 3, Vehicle Value: RM75000'),
                    ('H003', 'HEALTH', 'CUSTOM', 150000, 12000, 'Coverage Type: COMPREHENSIVE, Medical History: Minor asthma')
            ''')

            # Add test custom policies
            self.cursor.execute('''
                INSERT OR IGNORE INTO custom_policy (
                    customer_id, policy_id, agent_id, policy_type, policy_plan, 
                    coverage_amount, premium, status, start_date, end_date
                )
                VALUES 
                    -- Pending custom Life policy
                    ('970521125566', 'L003', 'AG01', 'LIFE', 'CUSTOM', 
                    450000, 20000, 'Pending request', '2024-01-01', '2025-01-01'),

                    -- Rejected custom Vehicle policy
                    ('010410150097', 'V003', 'AG02', 'VEHICLE', 'CUSTOM', 
                    75000, 2500, 'Rejected', '2024-01-15', '2025-01-15'),

                    -- Active custom Health policy
                    ('850317138494', 'H003', 'AG01', 'HEALTH', 'CUSTOM', 
                    150000, 12000, 'Accepted', '2024-02-01', '2025-02-01')
            ''')

            # Add Life Insurance Details test data
            self.cursor.execute('''
                INSERT OR IGNORE INTO life_policy_details (
                    policy_id, customer_id, beneficiary_name, death_benefit, medical_history
                )
                VALUES 
                    ('L001', 'C02', 'Mary Evans', 30000.00, 'None'),
                    ('L002', 'C03', 'John Smith', 300000.00, 'None'),
                    ('L003', 'C04', 'Sarah Lee', 450000.00, 'None')
            ''')

            # Add Vehicle Insurance Details test data
            self.cursor.execute('''
                INSERT OR IGNORE INTO vehicle_policy_details (
                    policy_id, customer_id, vehicle_type, vehicle_value, vehicle_age, 
                    vehicle_registration, accident_coverage
                    )
                VALUES 
                    ('V001', 'C02', 'Toyota Camry', 50000.00, 3, 'WXY 1234', 1),
                    ('V002', 'C04', 'BMW X5', 500000.00, 1, 'ABC 5678', 1),
                    ('V003', 'C03', 'Tesla Model 3', 75000.00, 0, 'DEF 9012', 1)
            ''')

            # Add Property Insurance Details test data
            self.cursor.execute('''
                INSERT OR IGNORE INTO property_policy_details (
                    policy_id, customer_id, property_address, property_type, property_value, property_age
                )
                VALUES 
                    ('P001', 'C02', '123 Oak Street, City', 'residential', 200000.00, 5),
                    ('P002', 'C01', '456 Pine Avenue, City', 'commercial', 2000000.00, 2)
            ''')

            # Add Health Insurance Details test data
            self.cursor.execute('''
                INSERT OR IGNORE INTO health_policy_details (
                    policy_id, customer_id, coverage_type, medical_history, deductible, copayment
                )
                VALUES 
                    ('H001', 'C02', 'BASIC', 'None', 1000.00, 20.00),
                    ('H002', 'C04', 'COMPREHENSIVE', 'None', 500.00, 10.00),
                    ('H003', 'C01', 'COMPREHENSIVE', 'Minor asthma', 1000.00, 15.00)
            ''')

            # Add test claims
            self.cursor.execute('''
                INSERT OR IGNORE INTO claims (claim_id, policy_id, customer_id, details, amount, status, date_filed)
                VALUES
                ('C01', 'V001', '970521125566', 'Car Accident Claim', 5000.00, 'Pending request', '2024-12-15'),
                ('C02', 'H001', '010410150097', 'House Fire Claim', 20000.00, 'Pending request', '2024-12-20'),
                ('C03', 'L001', '850317138494', 'Health Insurance Claim', 1200.00, 'Pending request', '2024-12-25');
            ''')

            self.conn.commit()
            print("Test data added successfully")

        except sqlite3.Error as e:
            print(f"Error adding test data: {e}")
            raise


def setup_database():
    # Main function to set up the database
    db = DatabaseManager()
    try:
        db.connect()
        db.init_database()
        db.add_test_data()
    except Exception as e:
        print(f"Database setup failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    setup_database()