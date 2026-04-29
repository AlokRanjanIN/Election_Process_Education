"""
Step-by-step voter registration guide service — state machine implementation.

Implements the registration workflow described in plan.md User Flows Section 2.
The state machine is fully deterministic and stateless on the server side:
the client passes current_state, and the server returns next_state + instructions.

State Flow:
  INIT -> DOCUMENTS_CHECKLIST -> FORM_SELECTION -> FORM_DOWNLOADED
       -> FORM_FILLING -> FORM_SUBMITTED -> VERIFICATION -> COMPLETE
"""

import logging
from typing import Dict, Optional

from models.guide import GuideResponse, GuideLink

logger = logging.getLogger(__name__)

# --- State Machine Definition ---
# Each state maps to: (step_number, next_state, instructions, links)

TOTAL_STEPS = 7

STATE_MACHINE: Dict[str, dict] = {
    "INIT": {
        "step_number": 1,
        "next_state": "DOCUMENTS_CHECKLIST",
        "instructions": (
            "Welcome to the voter registration process! "
            "Let's start by reviewing the documents you'll need. "
            "Please have the following ready:\n"
            "• Proof of Age (Birth Certificate, Class 10 Marksheet, or Passport)\n"
            "• Proof of Address (Aadhaar Card, Utility Bill, or Bank Passbook)\n"
            "• Passport-size photograph\n"
            "Click 'Next' when you have gathered these documents."
        ),
        "links": [
            {
                "type": "info",
                "url": "https://voters.eci.gov.in/",
                "label": "National Voters' Service Portal",
            }
        ],
    },
    "DOCUMENTS_CHECKLIST": {
        "step_number": 2,
        "next_state": "FORM_SELECTION",
        "instructions": (
            "Great! Now let's determine the right form for you:\n"
            "• Form 6 — For new voter registration (Indian residents)\n"
            "• Form 6A — For overseas (NRI) voter registration\n"
            "• Form 8 — For corrections in existing voter ID details\n"
            "• Form 7 — For objection to inclusion of a name in the electoral roll\n\n"
            "Most first-time voters need Form 6. "
            "Select your form and proceed to download it."
        ),
        "links": [
            {
                "type": "info",
                "url": "https://voters.eci.gov.in/forms",
                "label": "View All ECI Forms",
            }
        ],
    },
    "FORM_SELECTION": {
        "step_number": 3,
        "next_state": "FORM_DOWNLOADED",
        "instructions": (
            "Please download your selected form. "
            "You can fill it online on the National Voters' Service Portal, "
            "or download the PDF to fill manually.\n\n"
            "For online submission, visit the NVSP portal and click "
            "'Register as New Voter'."
        ),
        "links": [
            {
                "type": "download",
                "url": "https://voters.eci.gov.in/download/form6",
                "label": "Download Form 6 (PDF)",
            },
            {
                "type": "portal",
                "url": "https://www.nvsp.in/",
                "label": "NVSP Online Portal",
            },
        ],
    },
    "FORM_DOWNLOADED": {
        "step_number": 4,
        "next_state": "FORM_FILLING",
        "instructions": (
            "Fill in all required fields in the form carefully:\n"
            "• Full Name (as per ID proof)\n"
            "• Father's / Mother's / Husband's Name\n"
            "• Date of Birth\n"
            "• Current Residential Address\n"
            "• Constituency details (Part Number if known)\n\n"
            "Attach your passport-size photograph and self-attested copies "
            "of your ID and address proof documents."
        ),
        "links": [
            {
                "type": "info",
                "url": "https://voters.eci.gov.in/help/form6-instructions",
                "label": "Form 6 Filling Instructions",
            }
        ],
    },
    "FORM_FILLING": {
        "step_number": 5,
        "next_state": "FORM_SUBMITTED",
        "instructions": (
            "Submit your completed form through one of these methods:\n"
            "• Online: Upload via the NVSP portal\n"
            "• Offline: Submit at your nearest Electoral Registration Office (ERO)\n"
            "• By Post: Mail to the ERO of your constituency\n\n"
            "Keep a copy of the acknowledgment receipt for your records."
        ),
        "links": [
            {
                "type": "portal",
                "url": "https://www.nvsp.in/",
                "label": "Submit Online via NVSP",
            },
            {
                "type": "info",
                "url": "https://voters.eci.gov.in/ero-search",
                "label": "Find Your ERO Office",
            },
        ],
    },
    "FORM_SUBMITTED": {
        "step_number": 6,
        "next_state": "VERIFICATION",
        "instructions": (
            "Your form has been submitted! Here's what happens next:\n"
            "1. The ERO will verify your application\n"
            "2. A Booth Level Officer (BLO) may visit your address for verification\n"
            "3. Your name will be included in the draft electoral roll\n"
            "4. After final publication, you'll receive your EPIC (Voter ID) card\n\n"
            "This process typically takes 2-4 weeks. "
            "You can track your application status on the NVSP portal."
        ),
        "links": [
            {
                "type": "portal",
                "url": "https://www.nvsp.in/Forms/Forms/trackstatus",
                "label": "Track Application Status",
            }
        ],
    },
    "VERIFICATION": {
        "step_number": 7,
        "next_state": "COMPLETE",
        "instructions": (
            "Congratulations! Once verified, your EPIC (Voter ID) card will be issued.\n\n"
            "After receiving your EPIC:\n"
            "• Download the Voter Helpline App for easy access\n"
            "• Check your name in the Electoral Roll before election day\n"
            "• Find your polling station using the NVSP portal\n\n"
            "You are now a registered voter of India! "
            "Remember to exercise your right to vote in every election."
        ),
        "links": [
            {
                "type": "portal",
                "url": "https://electoralsearch.eci.gov.in/",
                "label": "Search Electoral Roll",
            },
            {
                "type": "download",
                "url": "https://play.google.com/store/apps/details?id=com.eci.citizen",
                "label": "Voter Helpline App",
            },
        ],
    },
    "COMPLETE": {
        "step_number": 7,
        "next_state": "COMPLETE",
        "instructions": (
            "You have completed the voter registration process! "
            "If you need to make corrections to your voter ID, "
            "you can submit Form 8 through the NVSP portal.\n\n"
            "For any issues, contact the ECI Voter Helpline: 1950"
        ),
        "links": [
            {
                "type": "portal",
                "url": "https://voters.eci.gov.in/",
                "label": "National Voters' Service Portal",
            }
        ],
    },
}


def get_valid_states() -> list[str]:
    """Return all valid states in the registration workflow."""
    return list(STATE_MACHINE.keys())


def get_next_step(current_state: str) -> Optional[GuideResponse]:
    """
    Retrieve the next step in the registration workflow.

    Args:
        current_state: The user's current state (e.g., "INIT", "FORM_DOWNLOADED").

    Returns:
        GuideResponse with instructions and next_state, or None if state is invalid.
    """
    state_upper = current_state.upper().strip()

    if state_upper not in STATE_MACHINE:
        logger.warning("Invalid guide state requested: %s", current_state)
        return None

    step = STATE_MACHINE[state_upper]
    logger.info(
        "Guide transition: %s -> %s (step %d/%d)",
        state_upper,
        step["next_state"],
        step["step_number"],
        TOTAL_STEPS,
    )

    links = [
        GuideLink(
            type=link["type"],
            url=link["url"],
            label=link.get("label"),
        )
        for link in step.get("links", [])
    ]

    return GuideResponse(
        current_state=state_upper,
        next_state=step["next_state"],
        instructions=step["instructions"],
        links=links,
        step_number=step["step_number"],
        total_steps=TOTAL_STEPS,
    )
