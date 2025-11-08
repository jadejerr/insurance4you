from enum import Enum
from datetime import datetime

class PolicyType(Enum):
    LIFE = "LIFE"
    VEHICLE = "VEHICLE"
    HEALTH = "HEALTH"
    PROPERTY = "PROPERTY"

class PolicyPlan(Enum):
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    CUSTOM = "CUSTOM"

def generate_policy_id(db, policy_type):
    """
    Generate a unique policy ID based on policy type.
    L#### for Life Insurance
    V#### for Vehicle Insurance
    H#### for Health Insurance
    P#### for Property Insurance
    """
    prefix_map = {
        PolicyType.LIFE.value: 'L',
        PolicyType.VEHICLE.value: 'V',
        PolicyType.HEALTH.value: 'H',
        PolicyType.PROPERTY.value: 'P'
    }

    prefix = prefix_map.get(policy_type, 'X')

    try:
        # Get the last policy ID for this type
        db.cursor.execute("""
            SELECT policy_id FROM policy_package 
            WHERE policy_id LIKE ? 
            ORDER BY policy_id DESC LIMIT 1
        """, (f'{prefix}%',))

        result = db.cursor.fetchone()

        if result:
            last_id = result[0]
            # Extract the number part and increment
            last_number = int(last_id[1:])
            new_number = last_number + 1
        else:
            # If no existing policies of this type, start with 1
            new_number = 1

        # Format the new policy ID with leading zeros (4 digits)
        return f"{prefix}{new_number:03d}"

    except Exception as e:
        print(f"Error generating policy ID: {e}")
        # Fallback ID in case of error
        return f"{prefix}{datetime.now().strftime('%Y%m%d%H%M%S')}"

class Insurance:
    def __init__(self, policy_type, policy_plan, coverage_amount, premium, start_date, end_date, status):
        self.policy_type = policy_type
        self.policy_plan = policy_plan
        self.coverage_amount = coverage_amount
        self.premium = premium
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        # policy_id will be set when saving to database
        self.policy_id = None

    def update_policy(self, db_manager, updates):
        """Update policy details in the database"""
        try:
            update_fields = []
            update_values = []

            for field, value in updates.items():
                if hasattr(self, field):
                    update_fields.append(f"{field} = ?")
                    update_values.append(value)
                    setattr(self, field, value)

            if update_fields:
                query = f"""
                    UPDATE purchased_policy 
                    SET {', '.join(update_fields)}
                    WHERE policy_id = ?
                """
                update_values.append(self.policy_id)
                db_manager.cursor.execute(query, update_values)
                db_manager.conn.commit()
                return True
        except Exception as e:
            print(f"Error updating policy: {e}")
            return False

    def cancel_policy(self, db_manager):
        """Cancel the policy in the database"""
        try:
            db_manager.cursor.execute("""
                UPDATE purchased_policy 
                SET status = 'Cancelled'
                WHERE policy_id = ?
            """, (self.policy_id,))

            db_manager.cursor.execute("""
                UPDATE purchased_policy 
                SET status = 'Cancelled'
                WHERE policy_id = ?
            """, (self.policy_id,))

            db_manager.conn.commit()
            self.status = 'Cancelled'
            return True
        except Exception as e:
            print(f"Error cancelling policy: {e}")
            return False

class LifeInsurance(Insurance):
    def __init__(self, policy_plan, coverage_amount, premium, start_date, end_date, status, beneficiary, death_benefit,
                 medical_history=""):
        super().__init__(PolicyType.LIFE.value, policy_plan, coverage_amount, premium, start_date, end_date, status)
        self.beneficiary = beneficiary
        self.death_benefit = death_benefit
        self.medical_history = medical_history

    def calculate_life_premium(self, age, coverage_amount):
        # Calculate life insurance premium based on age and coverage amount
        # Base monthly rate per RM1000 of coverage for a 25-year-old
        base_rate = 0.15  # RM0.15 per RM1000 of coverage per month

        # Age factor (increases as age increases)
        # At age 25, factor should be close to 1.0
        age_factor = 1 + ((age - 25) * 0.04)  # 4% increase for each year above 25
        if age < 25:
            age_factor = max(0.8, 1 - ((25 - age) * 0.02))  # 2% decrease for each year below 25, minimum 0.8

        # Coverage factor (slight increase for higher coverage amounts)
        coverage_factor = 1 + (coverage_amount / 1000000) * 0.1

        # Medical history factor (already handled in the class)
        medical_factor = 1.0 if not hasattr(self, 'medical_history') or self.medical_history.lower() == 'none' else 1.5

        # Calculate monthly premium
        monthly_premium = (coverage_amount / 1000) * base_rate * age_factor * coverage_factor * medical_factor

        # Convert to annual premium
        annual_premium = monthly_premium * 12

        return round(annual_premium, 2)

class VehicleInsurance(Insurance):
    def __init__(self, policy_plan, coverage_amount, premium, start_date, end_date, status, vehicle_details,
                 accident_coverage):
        super().__init__(PolicyType.VEHICLE.value, policy_plan, coverage_amount, premium, start_date, end_date, status)
        self.vehicle_details = vehicle_details
        self.accident_coverage = accident_coverage

    def calculate_vehicle_premium(self, vehicle_value, vehicle_age):
        # Calculate premium based on vehicle value and age
        # Base rate of 5% of vehicle value
        base_rate = 0.05
        # Age factor - increases premium for older vehicles
        age_factor = 1 + (vehicle_age * 0.1)  # 10% increase per year
        # Value factor - higher rates for more expensive vehicles
        value_factor = 1 + (vehicle_value / 100000)  # Increases with vehicle value

        annual_premium = vehicle_value * base_rate * age_factor * value_factor
        return round(annual_premium, 2)

    def process_accident_claim(self, db, claim_details, amount):
        # Process an accident claim
        try:
            claim_id = f"CLM{datetime.now().strftime('%Y%m%d%H%M%S')}"
            db_manager.cursor.execute("""
                INSERT INTO claims (claim_id, policy_id, details, amount, status)
                VALUES (?, ?, ?, ?, 'Pending request')
            """, (claim_id, self.policy_id, claim_details, amount))
            db_manager.conn.commit()
            return claim_id
        except Exception as e:
            print(f"Error processing claim: {e}")
            return None

class PropertyInsurance(Insurance):
    def __init__(self, policy_plan, coverage_amount, premium, start_date, end_date, status,
                 property_address, property_value, property_type):
        super().__init__(PolicyType.PROPERTY.value, policy_plan, coverage_amount, premium,
                         start_date, end_date, status)
        self.property_address = property_address
        self.property_value = property_value
        self.property_type = property_type

    def calculate_property_premium(self, property_value, property_age):
        # Calculate premium based on property value and age
        # Base rate of 0.3% of property value
        base_rate = 0.003
        # Age factor increases with property age
        age_factor = 1 + (property_age * 0.015)  # 1.5% increase per year
        # Value factor for expensive properties
        value_factor = 1 + (property_value / 1000000)
        risk_factor = self._calculate_risk_factor()

        annual_premium = property_value * base_rate * age_factor * value_factor * risk_factor
        return round(annual_premium, 2)

    def _calculate_risk_factor(self):
        # Calculate risk factor based on property type
        risk_factors = {
            'residential': 1.0,
            'commercial': 1.2,
            'industrial': 1.5
        }
        return risk_factors.get(self.property_type.lower(), 1.0)

class HealthInsurance(Insurance):
    def __init__(self, policy_plan, coverage_amount, premium, start_date, end_date, status,
                 coverage_type, deductible, copayment):
        super().__init__(PolicyType.HEALTH.value, policy_plan, coverage_amount, premium,
                         start_date, end_date, status)
        self.coverage_type = coverage_type.upper()
        self.deductible = deductible
        self.copayment = copayment

        # Define valid coverage types and their multipliers
        self.coverage_multipliers = {
            'BASIC': 1.0,  # Basic coverage (standard multiplier)
            'COMPREHENSIVE': 1.5,  # Comprehensive coverage (50% premium increase)
            'FAMILY': 2.0,  # Family coverage (100% premium increase)
            'INDIVIDUAL': 0.8,  # Individual coverage (20% discount)
            'HOSPITAL': 1.2,  # Hospital-only coverage (20% premium increase)
            'OUTPATIENT': 1.1,  # Outpatient coverage (10% premium increase)
            'SPECIALIST': 1.3  # Specialist coverage (30% premium increase)
        }

    def calculate_health_premium(self, age, medical_history="None"):
        # Calculate premium based on age, medical history, and coverage type
        # Base rate of 3% per RM1000 of coverage
        base_rate = 0.03

        # Age factor increases exponentially with age
        age_factor = 1 + (age * 0.025)  # 2.5% increase per year of age

        # Coverage factor based on total coverage amount
        coverage_factor = 1 + (self.coverage_amount / 100000)

        # Risk factor based on medical history
        risk_factor = self._calculate_risk_factor(medical_history)

        # Coverage type factor
        coverage_type_factor = self.coverage_multipliers.get(self.coverage_type, 1.0)

        # Calculate annual premium with all factors
        annual_premium = (
                (self.coverage_amount / 1000) *
                base_rate *
                age_factor *
                coverage_factor *
                risk_factor *
                coverage_type_factor
        )

        return round(annual_premium, 2)

    def _calculate_risk_factor(self, medical_history):
        # Calculate risk factor based on medical history
        if medical_history.lower() == "none":
            return 1.0
        return 1.8  # 80% increase for pre-existing conditions

    def get_coverage_description(self):
        # Return a description of what the coverage type includes
        coverage_descriptions = {
            'BASIC': "Covers essential medical services including regular check-ups and basic treatments",
            'COMPREHENSIVE': "Covers wide range of medical services including specialized treatments and procedures",
            'FAMILY': "Covers medical services for the entire family including spouse and children",
            'INDIVIDUAL': "Covers medical services for a single person with personalized care options",
            'HOSPITAL': "Focuses on hospitalization expenses including room charges and surgical procedures",
            'OUTPATIENT': "Covers medical care without hospital admission including clinic visits and day procedures",
            'SPECIALIST': "Covers visits to medical specialists and specialized treatments"
        }
        return coverage_descriptions.get(self.coverage_type, "Custom coverage plan")
