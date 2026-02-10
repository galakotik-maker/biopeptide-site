import unittest
import sys
import os
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.utils.law_loader import LawLoader
from backend.service.RegulatoryEngineService import RegulatoryEngineService

class TestRegulatoryEngine(unittest.TestCase):    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for the entire test class."""
        try:
            cls.law_loader = LawLoader()
            cls.engine = RegulatoryEngineService(cls.law_loader)
        except FileNotFoundError as e:
            raise unittest.SkipTest(f"Required data files not found: {e}")

    def test_01_gdpr_eu_enrichment(self):
        gdpr_law = self.engine.get_law_details("GDPR_EU")
        
        self.assertIsNotNone(gdpr_law, "GDPR_EU law should be loaded and found.")
        
        # Check required top-level fields
        self.assertIn("law_id", gdpr_law, "GDPR_EU should have law_id field.")
        self.assertIn("metadata", gdpr_law, "GDPR_EU should have metadata section.")
        self.assertIn("applicability", gdpr_law, "GDPR_EU should have applicability section.")
        self.assertIn("key_provisions", gdpr_law, "GDPR_EU should have key_provisions section.")
        
        # Check specific GDPR provisions
        key_provisions = gdpr_law["key_provisions"]
        self.assertIn("Lawful_Basis_for_Processing", key_provisions)
        self.assertIn("Data_Subject_Rights", key_provisions)
        
        # Verify provision structure
        lawful_basis = key_provisions["Lawful_Basis_for_Processing"]
        self.assertIn("section", lawful_basis)
        self.assertIn("description", lawful_basis)
        self.assertIn("requirements", lawful_basis)
        self.assertIn("ai_prompt_guidance", lawful_basis)

    def test_02_pdpa_my_enrichment(self):
        pdpa_law = self.engine.get_law_details("PDPA_MY")
        self.assertIsNotNone(pdpa_law, "PDPA_MY law should be loaded.")
        
        key_provisions = pdpa_law.get("key_provisions", {})
        self.assertIn("Notice_And_Choice_Principle", key_provisions)
        
        notice_provision = key_provisions["Notice_And_Choice_Principle"]
        self.assertIn("requirements", notice_provision)
        
        expected_requirement = "Must describe the personal data being collected."
        actual_requirements = [req.strip() for req in notice_provision["requirements"]]
        self.assertIn(expected_requirement, actual_requirements)

    def test_03_ccpa_us_enrichment(self):
        ccpa_law = self.engine.get_law_details("CCPA_US")
        self.assertIsNotNone(ccpa_law, "CCPA_US law should be loaded.")
        
        # Check metadata
        metadata = ccpa_law["metadata"]
        self.assertIn("California Consumer Privacy Act", metadata["name"])
        self.assertEqual(metadata["jurisdiction"], "US")
        
        # Check CCPA-specific provisions
        key_provisions = ccpa_law["key_provisions"]
        self.assertIn("Consumer_Rights", key_provisions)
        
        # Verify California-specific consumer rights
        consumer_rights = key_provisions["Consumer_Rights"]
        requirements = consumer_rights["requirements"]
        self.assertTrue(any("Right to Know" in req for req in requirements))
        self.assertTrue(any("Right to Delete" in req for req in requirements))
        self.assertTrue(any("Right to Opt-Out" in req for req in requirements))

    def test_04_employment_act_my_enrichment(self):
        employment_law = self.engine.get_law_details("EMPLOYMENT_ACT_MY")
        self.assertIsNotNone(employment_law, "EMPLOYMENT_ACT_MY law should be loaded.")
        
        metadata = employment_law["metadata"]
        self.assertIn("Employment Act 1955", metadata["name"])
        self.assertEqual(metadata["jurisdiction"], "MY")

    def test_05_pdpa_sg_enrichment(self):
        pdpa_sg_law = self.engine.get_law_details("PDPA_SG")
        self.assertIsNotNone(pdpa_sg_law, "PDPA_SG law should be loaded.")
        
        metadata = pdpa_sg_law["metadata"]
        self.assertIn("Personal Data Protection Act", metadata["name"])
        self.assertEqual(metadata["jurisdiction"], "SG")

    def test_06_jurisdiction_mapping_correctness(self):
        # Test EU jurisdiction
        eu_laws = self.engine.get_laws_for_jurisdiction("EU")
        self.assertIn("GDPR_EU", eu_laws.keys())
        
        # Test MY jurisdiction
        my_laws = self.engine.get_laws_for_jurisdiction("MY")
        self.assertIn("PDPA_MY", my_laws.keys())
        self.assertIn("EMPLOYMENT_ACT_MY", my_laws.keys())
        
        # Test US jurisdiction
        us_laws = self.engine.get_laws_for_jurisdiction("US")
        self.assertIn("CCPA_US", us_laws.keys())
        
        # Test SG jurisdiction
        sg_laws = self.engine.get_laws_for_jurisdiction("SG")
        self.assertIn("PDPA_SG", sg_laws.keys())

    def test_07_compliance_checklist_structure(self):
        # Test EU Data Processing Agreement
        eu_checklist = self.engine.get_compliance_checklist("EU", "Data Processing Agreement")
        self.assertIn("GDPR_EU", eu_checklist)
        
        gdpr_checklist_data = eu_checklist["GDPR_EU"]
        self.assertIn("metadata", gdpr_checklist_data)
        self.assertIn("key_provisions", gdpr_checklist_data)
        
        # Verify provisions are detailed dictionaries
        key_provisions = gdpr_checklist_data["key_provisions"]
        self.assertIsInstance(key_provisions["Lawful_Basis_for_Processing"], dict)
        
        # Test Malaysian employment contract
        my_checklist = self.engine.get_compliance_checklist("MY", "Employment Contract")
        self.assertIn("PDPA_MY", my_checklist)
        self.assertIn("EMPLOYMENT_ACT_MY", my_checklist)

    def test_08_all_law_files_have_required_fields(self):
        law_files = ["GDPR_EU", "PDPA_MY", "CCPA_US", "EMPLOYMENT_ACT_MY", "PDPA_SG"]
        
        for law_id in law_files:
            law_data = self.engine.get_law_details(law_id)
            self.assertIsNotNone(law_data, f"{law_id} should be loaded.")
            
            # Check required top-level fields
            self.assertIn("law_id", law_data, f"{law_id} should have law_id field.")
            self.assertIn("metadata", law_data, f"{law_id} should have metadata section.")
            
            # Check metadata fields
            metadata = law_data["metadata"]
            self.assertIn("name", metadata, f"{law_id} metadata should have name.")
            self.assertIn("jurisdiction", metadata, f"{law_id} metadata should have jurisdiction.")
            self.assertIn("type", metadata, f"{law_id} metadata should have type.")
            
            # Verify name is valid
            law_name = metadata["name"]
            self.assertIsNotNone(law_name, f"{law_id} name should not be None.")
            self.assertIsInstance(law_name, str, f"{law_id} name should be a string.")
            self.assertTrue(len(law_name) > 0, f"{law_id} name should not be empty.")

    def test_09_ai_prompt_guidance_availability(self):
        # Check GDPR_EU provisions
        gdpr_law = self.engine.get_law_details("GDPR_EU")
        key_provisions = gdpr_law["key_provisions"]
        
        for provision_name, provision_data in key_provisions.items():
            if isinstance(provision_data, dict):
                self.assertIn("ai_prompt_guidance", provision_data, 
                              f"GDPR provision {provision_name} should have AI prompt guidance.")
                guidance = provision_data["ai_prompt_guidance"]
                self.assertIsInstance(guidance, str, "AI prompt guidance should be a string.")
                self.assertTrue(len(guidance) > 50, "AI prompt guidance should be substantial.")
        
        # Check PDPA_MY provisions
        pdpa_law = self.engine.get_law_details("PDPA_MY")
        key_provisions = pdpa_law["key_provisions"]
        
        consent_provision = key_provisions.get("General_And_Consent_Principle")
        if consent_provision:
            self.assertIn("ai_prompt_guidance", consent_provision, 
                          "PDPA consent provision should have AI prompt guidance.")

    def test_10_contract_type_filtering(self):
        # Test employment-specific laws for employment contracts
        my_employment_checklist = self.engine.get_compliance_checklist("MY", "Employment Contract")
        self.assertIn("EMPLOYMENT_ACT_MY", my_employment_checklist, 
                      "Employment contracts should include Employment Act.")
        
        # Test data protection laws for data processing agreements
        eu_data_checklist = self.engine.get_compliance_checklist("EU", "Data Processing Agreement")
        self.assertIn("GDPR_EU", eu_data_checklist, 
                      "Data processing agreements should include GDPR.")


if __name__ == '__main__':
    unittest.main(verbosity=2)