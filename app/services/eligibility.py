class EligibilityEngine:
    @staticmethod
    def _normalize(val):
        """Helper to sanitize strings for better logic hits"""
        if isinstance(val, str):
            return val.strip().lower()
        if isinstance(val, list):
            return [str(v).strip().lower() for v in val]
        return val

    @staticmethod
    def evaluate(user_data: dict, scheme: dict):
        """
        Fuzzy Eligibility filter.
        Returns: (is_eligible, confidence_score, match_reason, match_type)
        """
        eligibility_data = scheme.get("eligibility", {})
        logic_rules = eligibility_data.get("logic_rules", [])
        
        total_conditions = len(logic_rules)
        if total_conditions == 0:
            # If there are no conditions, they are unconditionally eligible
            return True, 1.0, "No specific conditions apply.", "Full"
            
        matched_conditions = 0
        reasons = []

        for rule in logic_rules:
            field = rule.get("field")
            operator = rule.get("operator")
            expected_value = rule.get("value")
            
            if field not in user_data or user_data[field] is None:
                reasons.append(f"Missing '{field}' profile data")
                continue
                
            user_val = user_data[field]
            
            # Normalize strings for safety
            norm_user = EligibilityEngine._normalize(user_val)
            norm_expected = EligibilityEngine._normalize(expected_value)
            
            # Safe Operator Evaluation
            match = False
            if operator == "==":
                match = (norm_user == norm_expected)
            elif operator == "!=":
                match = (norm_user != norm_expected)
            elif operator == ">":
                match = (user_val > expected_value)
            elif operator == "<":
                match = (user_val < expected_value)
            elif operator == ">=":
                match = (user_val >= expected_value)
            elif operator == "<=":
                match = (user_val <= expected_value)
            elif operator == "in":
                # norm_expected must be a list
                match = (norm_user in norm_expected)
                
            if match:
                matched_conditions += 1
                reasons.append(f"Matched {field}")
            else:
                reasons.append(f"Failed {field} ({operator} {expected_value})")

        confidence_score = matched_conditions / total_conditions
        
        # Classification Mapping Based on Confidence Band
        if confidence_score == 1.0:
            match_type = "Full"
            is_eligible = True
            match_reason = "Strong Match: User perfectly fits criteria. " + ", ".join([r for r in reasons if "Matched" in r])
        elif confidence_score >= 0.6:
            match_type = "Partial"
            is_eligible = True
            match_reason = "Partial Match: " + ", ".join(reasons)
        else:
            match_type = "Low"
            is_eligible = False
            match_reason = "Did not meet required thresholds. " + ", ".join([r for r in reasons if "Failed" in r])

        return is_eligible, confidence_score, match_reason, match_type

eligibility_engine = EligibilityEngine()
