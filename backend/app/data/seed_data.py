from typing import List, Dict
from app.schemas.models import (
    Service,
    DocumentType,
    UserDocument,
    DocumentStatus,
    Application,
    ApplicationStatus,
    ApplicationStep,
)

# Seed Document & Information Types
SEED_DOCUMENT_TYPES: Dict[str, DocumentType] = {
    "identity_proof": DocumentType(
        id="identity_proof",
        code="identity_proof",
        name="Identity Proof",
        description="Official government-issued identification verifying your legal identity.",
        accepted_examples=["Aadhaar Card", "Passport", "Voter ID", "PAN Card"],
        is_information_item=False
    ),
    "address_proof": DocumentType(
        id="address_proof",
        code="address_proof",
        name="Address Proof",
        description="Document verifying your current residential address.",
        accepted_examples=["Registered Rent Agreement", "Electricity/Water Utility Bill", "Bank Passbook/Statement", "Property Tax Receipt"],
        is_information_item=False
    ),
    "vehicle_reg": DocumentType(
        id="vehicle_reg",
        code="vehicle_reg",
        name="Vehicle Registration Document",
        description="Registration Certificate (RC) for your motor vehicle.",
        accepted_examples=["Vehicle Registration Certificate (RC)", "Form 23", "Smart Card RC"],
        is_information_item=False
    ),
    "pds_ration_card": DocumentType(
        id="pds_ration_card",
        code="pds_ration_card",
        name="PDS / Ration Card",
        description="Public Distribution System ration card issued by Civil Supplies.",
        accepted_examples=["Existing State Ration Card", "BPL/AAY Card", "E-Ration Card Acknowledgement"],
        is_information_item=False
    ),
    "txn_details": DocumentType(
        id="txn_details",
        code="txn_details",
        name="Transaction & Account Reference Information",
        description="Transaction ID, timestamp, bank account/UPI ID, and SMS or payment alert record.",
        accepted_examples=["UPI Transaction Ref / UTR Number", "Bank Debit Alert SMS", "Payment App Statement Screenshot"],
        is_information_item=True
    ),
    "marriage_proof": DocumentType(
        id="marriage_proof",
        code="marriage_proof",
        name="Marriage Proof & Joint Particulars",
        description="Wedding invitation card, joint photograph, and identification of 2 witnesses.",
        accepted_examples=["Wedding Invitation Card", "Joint Marriage Photo", "Witness Identity Proofs"],
        is_information_item=False
    ),
    "hospital_death_report": DocumentType(
        id="hospital_death_report",
        code="hospital_death_report",
        name="Medical Death Report / Institutional Intimation",
        description="Hospital cause-of-death report or cremation/burial authority certificate.",
        accepted_examples=["Hospital Cause of Death Certificate", "Cremation/Burial Ground Intimation Receipt", "Attending Doctor Certificate"],
        is_information_item=False
    ),
}

# Seed Prototype & Official Services across all 4 scenarios
SEED_SERVICES: Dict[str, Service] = {
    # 1. Relocation Services
    "address_update": Service(
        id="address_update",
        name="Address Update",
        category="Civil Registry & Identification",
        description="Update your official residential address across national and municipal identity registries.",
        why_relevant="You indicated a change of residence. Keeping your official address updated ensures uninterrupted civic services, banking communications, and localized benefits.",
        required_document_ids=["identity_proof", "address_proof"],
        basic_steps=[
            "Prepare identity proof and valid new address proof (rent agreement/utility bill).",
            "Fill out the online address modification request form.",
            "Upload self-attested copies of supporting proof documents.",
            "Submit the update request and retain the tracking reference for status updates."
        ],
        applicable_life_events=["relocation", "marriage"],
        portal_name="National Identity & Address Portal",
        portal_url="https://services.india.gov.in",
        is_mock_portal=False,
        estimated_processing_days=7,
        mock_status=ApplicationStatus.COMPLETED
    ),
    "pds_update": Service(
        id="pds_update",
        name="PDS / Ration-related Update",
        category="Food & Civil Supplies",
        description="Transfer your Public Distribution System (PDS) ration card quota to your new fair price shop jurisdiction.",
        why_relevant="You indicated that you receive food/PDS benefits. Updating your ration record helps transfer your quota to your new locality.",
        required_document_ids=["identity_proof", "address_proof", "pds_ration_card"],
        basic_steps=[
            "Obtain surrender certificate or migration acknowledgment from previous fair price shop.",
            "Submit relocation intimation with the local Food & Civil Supplies office.",
            "Verify family member details and provide new address verification proof.",
            "Receive new fair price shop assignment and updated ration card record."
        ],
        applicable_life_events=["relocation"],
        portal_name="State Food & Civil Supplies Department (Prototype)",
        portal_url="/prototype-portal/pds-update",
        is_mock_portal=True,
        estimated_processing_days=14,
        mock_status=ApplicationStatus.UNDER_REVIEW
    ),
    "vehicle_update": Service(
        id="vehicle_update",
        name="Vehicle-related Address/Record Update",
        category="Transport & Motor Vehicles",
        description="Record your new residential address on your Motor Vehicle Registration Certificate (RC) with the Regional Transport Office (RTO).",
        why_relevant="You indicated vehicle ownership. Updating your vehicle Registration Certificate (RC) records your new residence with the local transport office.",
        required_document_ids=["identity_proof", "address_proof", "vehicle_reg"],
        basic_steps=[
            "Obtain NOC (No Objection Certificate) from previous RTO if shifting between distinct RTO jurisdictions.",
            "Submit Form 33 (Application for change of address in Registration Certificate).",
            "Submit chassis pencil print, valid PUC (Pollution Under Control), insurance, and new address proof.",
            "Pay administrative RTO fees and receive the updated RC Smart Card."
        ],
        applicable_life_events=["relocation"],
        portal_name="Transport Department / Parivahan (Prototype)",
        portal_url="/prototype-portal/vehicle-update",
        is_mock_portal=True,
        estimated_processing_days=15,
        mock_status=ApplicationStatus.ACTION_REQUIRED
    ),
    "benefits_review": Service(
        id="benefits_review",
        name="Government Benefits Review",
        category="Social Welfare & Schemes",
        description="Explore location-specific municipal and state welfare schemes available to residents at your new destination.",
        why_relevant="Moving to a new municipal jurisdiction can unlock access to local civic welfare schemes, health cards, senior citizen passes, and education grants.",
        required_document_ids=["identity_proof", "address_proof"],
        basic_steps=[
            "Explore local district social welfare catalogs and municipal schemes.",
            "Check specific residential duration, income, and category criteria.",
            "Submit scheme enrollment requests through the district single-window portal."
        ],
        applicable_life_events=["relocation"],
        portal_name="Citizen Social Welfare Discovery Portal (Prototype)",
        portal_url="/prototype-portal/benefits-review",
        is_mock_portal=True,
        estimated_processing_days=5,
        mock_status=ApplicationStatus.NOT_STARTED
    ),

    # 2. Financial Fraud Services
    "financial_fraud_reporting": Service(
        id="financial_fraud_reporting",
        name="Financial Cyber Fraud Reporting",
        category="Cybercrime & Consumer Protection",
        description="Report unauthorized financial transactions, UPI fraud, or cyber theft to the National Cyber Crime Reporting Portal and financial intermediaries.",
        why_relevant="You reported an unauthorized transaction. Reporting immediately to the national cybercrime portal initiates an inter-bank dispute hold to prevent further loss.",
        required_document_ids=["txn_details", "identity_proof"],
        basic_steps=[
            "Immediately contact your bank customer service or payment app helpline to freeze the affected account/card/UPI ID.",
            "Collect transaction reference numbers (UTR), alert SMS timestamps, and beneficiary payment details.",
            "File an incident complaint on the official National Cyber Crime Reporting Portal (cybercrime.gov.in) or call National Helpline 1930.",
            "Save the formal Acknowledgment Receipt and furnish a copy to your home bank branch for chargeback processing."
        ],
        applicable_life_events=["financial_fraud"],
        portal_name="National Cyber Crime Reporting Portal (cybercrime.gov.in)",
        portal_url="https://cybercrime.gov.in",
        is_mock_portal=False,
        estimated_processing_days=3,
        mock_status=ApplicationStatus.ACTION_REQUIRED
    ),

    # 3. Marriage Services
    "marriage_registration": Service(
        id="marriage_registration",
        name="Marriage Registration",
        category="Civil Registry & Vital Statistics",
        description="Register your marriage with the local Registrar of Marriages / Municipal Corporation to obtain a legal Marriage Certificate.",
        why_relevant="You recently got married. An official Marriage Certificate serves as legal proof of marriage for joint administrative records, identity updates, and civic benefits.",
        required_document_ids=["identity_proof", "address_proof", "marriage_proof"],
        basic_steps=[
            "Fill the online memorandum of marriage application through your State or Municipal Civil Registration Portal.",
            "Attach joint photographs, wedding card/proof, identity documents, and witness particulars.",
            "Book an appointment and appear before the Sub-Registrar / Municipal Officer with 2 witnesses.",
            "Receive the digitally verified official Marriage Certificate."
        ],
        applicable_life_events=["marriage"],
        portal_name="National Government Services Portal / Civil Registration",
        portal_url="https://services.india.gov.in",
        is_mock_portal=False,
        estimated_processing_days=10,
        mock_status=ApplicationStatus.NOT_STARTED
    ),
    "aadhaar_update": Service(
        id="aadhaar_update",
        name="Aadhaar Demographic Update",
        category="Civil Registry & Identification",
        description="Update demographic details such as updated surname, marital status name change, or residential address in the UIDAI Aadhaar registry.",
        why_relevant="Your marriage or life transition may have resulted in changes to your name or residential address. Updating your Aadhaar demographic record keeps all linked civic records in sync.",
        required_document_ids=["identity_proof", "address_proof"],
        basic_steps=[
            "Visit the official UIDAI myAadhaar portal and login using your Aadhaar number and registered mobile OTP.",
            "Select 'Update Demographic Data' (Name / Address / Marital Details).",
            "Upload valid supporting documents (Marriage Certificate for name changes, valid address proof for address changes).",
            "Submit the update request and track status using the Service Request Number (SRN)."
        ],
        applicable_life_events=["marriage", "relocation"],
        portal_name="UIDAI myAadhaar Portal (uidai.gov.in)",
        portal_url="https://myaadhaar.uidai.gov.in",
        is_mock_portal=False,
        estimated_processing_days=7,
        mock_status=ApplicationStatus.NOT_STARTED
    ),

    # 4. Family Death Services
    "death_registration": Service(
        id="death_registration",
        name="Death Registration & Certificate",
        category="Civil Registry & Vital Statistics",
        description="Register the demise of a family member with the municipal health department or registrar of births & deaths to obtain the official Death Certificate.",
        why_relevant="Registering a family member's demise is the foundational civil requirement before settling survivor benefits, family pensions, or estate records.",
        required_document_ids=["hospital_death_report", "identity_proof"],
        basic_steps=[
            "Obtain the official cause-of-death certificate from the hospital or cremation/burial ground intimation.",
            "Submit the death registration application to the local municipal registrar of births & deaths.",
            "Provide the identity proofs of the deceased and the reporting family member.",
            "Collect the official Death Certificate for legal, pension, and banking closures."
        ],
        applicable_life_events=["family_death"],
        portal_name="Civil Registration System (CRS - crsorgi.gov.in)",
        portal_url="https://crsorgi.gov.in",
        is_mock_portal=False,
        estimated_processing_days=5,
        mock_status=ApplicationStatus.ACTION_REQUIRED
    ),
    "pension_survivor_review": Service(
        id="pension_survivor_review",
        name="Pension & Survivor Benefits Review",
        category="Social Welfare & Pensions",
        description="Intimate pension disbursing authorities and social welfare departments to initiate family pension, nominee settlements, and survivor welfare claims.",
        why_relevant="If the deceased was a government pensioner or eligible for social welfare, intimating the authority initiates survivor pension and nominee transitions.",
        required_document_ids=["hospital_death_report", "identity_proof"],
        basic_steps=[
            "Submit an intimation of demise accompanied by a certified copy of the Death Certificate to the pension sanctioning authority or bank branch.",
            "Submit Form 14 (Application for Family Pension) along with nominee details and bank mandate.",
            "Complete verification to initiate family pension disbursements."
        ],
        applicable_life_events=["family_death"],
        portal_name="Central & State Pensioners Portal",
        portal_url="https://pensionersportal.gov.in",
        is_mock_portal=False,
        estimated_processing_days=30,
        mock_status=ApplicationStatus.NOT_STARTED
    ),
}

# Initial Demo User Document State
DEMO_USER_ID = "usr_demo_citizen"

SEED_USER_DOCUMENTS: Dict[str, UserDocument] = {
    "identity_proof": UserDocument(
        id="udoc_1",
        user_id=DEMO_USER_ID,
        document_type_id="identity_proof",
        document_name="Identity Proof (Aadhaar Card)",
        status=DocumentStatus.AVAILABLE,
        updated_at="2026-08-20T10:00:00Z",
        is_information_item=False
    ),
    "address_proof": UserDocument(
        id="udoc_2",
        user_id=DEMO_USER_ID,
        document_type_id="address_proof",
        document_name="Address Proof (Registered Rental Agreement)",
        status=DocumentStatus.AVAILABLE,
        updated_at="2026-08-22T14:30:00Z",
        is_information_item=False
    ),
    "vehicle_reg": UserDocument(
        id="udoc_3",
        user_id=DEMO_USER_ID,
        document_type_id="vehicle_reg",
        document_name="Vehicle Registration Document (RC)",
        status=DocumentStatus.MISSING,
        updated_at=None,
        is_information_item=False
    ),
    "pds_ration_card": UserDocument(
        id="udoc_4",
        user_id=DEMO_USER_ID,
        document_type_id="pds_ration_card",
        document_name="PDS / Ration Card",
        status=DocumentStatus.MISSING,
        updated_at=None,
        is_information_item=False
    ),
    "txn_details": UserDocument(
        id="udoc_5",
        user_id=DEMO_USER_ID,
        document_type_id="txn_details",
        document_name="Transaction Reference & Payment Details",
        status=DocumentStatus.MISSING,
        updated_at=None,
        is_information_item=True
    ),
    "marriage_proof": UserDocument(
        id="udoc_6",
        user_id=DEMO_USER_ID,
        document_type_id="marriage_proof",
        document_name="Marriage Proof & Joint Particulars",
        status=DocumentStatus.MISSING,
        updated_at=None,
        is_information_item=False
    ),
    "hospital_death_report": UserDocument(
        id="udoc_7",
        user_id=DEMO_USER_ID,
        document_type_id="hospital_death_report",
        document_name="Medical Death Report / Institutional Intimation",
        status=DocumentStatus.MISSING,
        updated_at=None,
        is_information_item=False
    ),
}

# Seed Demo Applications
SEED_APPLICATIONS: Dict[str, Application] = {
    "app_addr_01": Application(
        id="app_addr_01",
        user_id=DEMO_USER_ID,
        service_id="address_update",
        service_name="Address Update",
        category="Civil Registry & Identification",
        status=ApplicationStatus.COMPLETED,
        tracking_number="MH-2026-ADDR-9104",
        applied_date="2026-08-15",
        estimated_completion_date="2026-08-22",
        remarks="Address verified and updated across central registry.",
        steps=[
            ApplicationStep(step_order=1, title="Application Submitted", description="Documents uploaded and application submitted.", is_completed=True),
            ApplicationStep(step_order=2, title="Document Verification", description="Aadhaar and rental deed verified by registrar.", is_completed=True),
            ApplicationStep(step_order=3, title="Address Updated", description="Official record updated in municipal registry.", is_completed=True)
        ]
    ),
    "app_pds_02": Application(
        id="app_pds_02",
        user_id=DEMO_USER_ID,
        service_id="pds_update",
        service_name="PDS / Ration-related Update",
        category="Food & Civil Supplies",
        status=ApplicationStatus.UNDER_REVIEW,
        tracking_number="MH-2026-PDS-4821",
        applied_date="2026-08-24",
        estimated_completion_date="2026-09-07",
        remarks="Application received; awaiting jurisdictional transfer approval from destination Tehsil office.",
        steps=[
            ApplicationStep(step_order=1, title="Transfer Request Initiated", description="Surrender acknowledgment submitted.", is_completed=True),
            ApplicationStep(step_order=2, title="Under Review at Tehsil", description="Verification of local family member allocation.", is_completed=False),
            ApplicationStep(step_order=3, title="Fair Price Shop Assigned", description="New shop quota activation.", is_completed=False)
        ]
    ),
    "app_veh_03": Application(
        id="app_veh_03",
        user_id=DEMO_USER_ID,
        service_id="vehicle_update",
        service_name="Vehicle-related Address/Record Update",
        category="Transport & Motor Vehicles",
        status=ApplicationStatus.ACTION_REQUIRED,
        tracking_number="MH-2026-RTO-7203",
        applied_date="2026-08-26",
        estimated_completion_date="2026-09-10",
        remarks="Action Required: Please upload clear copy of Vehicle Registration Certificate (RC) to proceed.",
        steps=[
            ApplicationStep(step_order=1, title="Form 33 Drafted", description="Change of address drafted.", is_completed=True),
            ApplicationStep(step_order=2, title="Action Required: Upload RC", description="Original or clear digital RC copy required.", is_completed=False),
            ApplicationStep(step_order=3, title="RTO Inspection & Endorsement", description="Endorsement of new address in Vahan registry.", is_completed=False)
        ]
    ),
    "app_ben_04": Application(
        id="app_ben_04",
        user_id=DEMO_USER_ID,
        service_id="benefits_review",
        service_name="Government Benefits Review",
        category="Social Welfare & Schemes",
        status=ApplicationStatus.NOT_STARTED,
        tracking_number="MH-2026-BEN-0000",
        applied_date=None,
        estimated_completion_date=None,
        remarks="Not Started. Review available schemes at your convenience.",
        steps=[
            ApplicationStep(step_order=1, title="Scheme Discovery", description="Review local welfare schemes.", is_completed=False),
            ApplicationStep(step_order=2, title="Eligibility Verification", description="Verify residential and category criteria.", is_completed=False)
        ]
    ),
    "app_fraud_05": Application(
        id="app_fraud_05",
        user_id=DEMO_USER_ID,
        service_id="financial_fraud_reporting",
        service_name="Financial Cyber Fraud Reporting",
        category="Cybercrime & Consumer Protection",
        status=ApplicationStatus.ACTION_REQUIRED,
        tracking_number="NCR-2026-FRAUD-1930",
        applied_date="2026-08-28",
        estimated_completion_date="2026-08-31",
        remarks="Action Required: File incident report on cybercrime.gov.in and notify your bank's fraud desk with the complaint reference.",
        steps=[
            ApplicationStep(step_order=1, title="Block Account / Payment Instrument", description="Freeze affected UPI ID / card.", is_completed=True),
            ApplicationStep(step_order=2, title="File Cybercrime Incident Report", description="Submit on cybercrime.gov.in or call 1930.", is_completed=False),
            ApplicationStep(step_order=3, title="Bank Dispute Initiation", description="Provide cyber complaint acknowledgment to bank.", is_completed=False)
        ]
    ),
    "app_marriage_06": Application(
        id="app_marriage_06",
        user_id=DEMO_USER_ID,
        service_id="marriage_registration",
        service_name="Marriage Registration",
        category="Civil Registry & Vital Statistics",
        status=ApplicationStatus.NOT_STARTED,
        tracking_number="MRG-2026-CIVIL-0000",
        applied_date=None,
        estimated_completion_date=None,
        remarks="Ready to initiate. Collect marriage proof and witness documents.",
        steps=[
            ApplicationStep(step_order=1, title="Online Application Drafted", description="Fill memorandum of marriage.", is_completed=False),
            ApplicationStep(step_order=2, title="Registrar Verification & Signature", description="Physical appearance with 2 witnesses.", is_completed=False)
        ]
    ),
    "app_death_07": Application(
        id="app_death_07",
        user_id=DEMO_USER_ID,
        service_id="death_registration",
        service_name="Death Registration & Certificate",
        category="Civil Registry & Vital Statistics",
        status=ApplicationStatus.ACTION_REQUIRED,
        tracking_number="CRS-2026-DTH-1029",
        applied_date="2026-08-27",
        estimated_completion_date="2026-09-01",
        remarks="Action Required: Obtain hospital death report and submit registration with municipal registrar.",
        steps=[
            ApplicationStep(step_order=1, title="Medical Death Report Obtained", description="Cause-of-death intimation verified.", is_completed=True),
            ApplicationStep(step_order=2, title="Municipal Registration Form Submitted", description="Pending registrar issuance of certified certificate.", is_completed=False)
        ]
    ),
}
