from typing import Dict, List

KEYWORDS: Dict[str, List[str]] = {
    "maintenance_and_repair": [
        "maintenance", "repair", "repairs", "repair and maintenance",
        "aftermarket service", "after-sales service", "after sales service",
        "field service", "mro", "maintenance overhaul", "overhaul",
        "service and repair", "servicing", "product servicing",
        "scheduled maintenance", "unscheduled maintenance"
    ],

    "spare_parts_support": [
        "spare parts", "replacement parts", "parts support",
        "parts and service", "parts sales", "component parts",
        "aftermarket parts", "parts distribution", "parts logistics",
        "genuine parts", "parts supply", "parts fulfillment"
    ],

    "leasing_and_rental": [
        "lease", "leasing", "operating lease", "capital lease",
        "rental", "rentals", "equipment rental",
        "power by the hour", "power-by-the-hour",
        "fee per use", "usage-based pricing", "subscription service",
        "as-a-service", "aaS", "equipment-as-a-service"
    ],

    "warranty_and_insurance": [
        "warranty", "extended warranty", "warranty service",
        "product warranty", "service warranty",
        "insurance", "product insurance", "coverage plan"
    ],

    "installation_and_commissioning": [
        "installation", "installing", "commissioning",
        "system installation", "equipment installation",
        "assembly", "setup", "on-site installation",
        "deployment service"
    ],

    "technical_support": [
        "technical support", "tech support", "support services",
        "customer support", "helpdesk", "troubleshooting",
        "remote support", "call center support", "24/7 support",
        "service hotline", "technical assistance"
    ],

    "customization_and_r&d_services": [
        "customization", "customized solutions", "customised solutions",
        "tailored solution", "bespoke solution",
        "engineering services", "engineering design",
        "r&d services", "research and development service",
        "product adaptation", "system tailoring"
    ],

    "distribution_and_procurement": [
        "distribution", "product distribution", "distribution services",
        "procurement", "purchasing services", "supply procurement",
        "trade and distribution", "inventory procurement",
        "material sourcing", "logistics service", "fulfillment services"
    ],

    "training_and_consulting": [
        "training", "training services", "skills training",
        "consulting", "consultancy", "professional consulting",
        "customer training", "technical training",
        "education services", "on-site training", "certification training"
    ],

    "solutions_system_integration": [
        "solution", "solutions", "integrated solution",
        "system integration", "integration services",
        "turnkey solution", "system architecture",
        "end-to-end solution", "platform integration"
    ],

    "digital_and_streaming_services": [
        "software as a service", "saas", "cloud service",
        "digital services", "digital platform",
        "streaming services", "online services",
        "remote monitoring service", "iot service",
        "data analytics service", "cloud-based service"
    ],

    "performance_based_contracts": [
        "performance-based", "performance based",
        "performance contract", "performance guarantee",
        "pay per use", "fee per use", "pay-per-hour",
        "service-level agreement", "sla contract",
        "availability guarantee", "uptime guarantee"
    ],

    "recycling_and_process_management": [
        "recycling", "recycle services", "recycling program",
        "process management", "waste management",
        "resource recovery", "end-of-life services",
        "asset disposal", "equipment disposal", "reverse logistics"
    ]
}

CATEGORY_TYPE: Dict[str, str] = {
    "maintenance_and_repair": "complementing",
    "spare_parts_support": "complementing",
    "warranty_and_insurance": "complementing",
    "installation_and_commissioning": "complementing",
    "technical_support": "complementing",
    "training_and_consulting": "complementing",
    "distribution_and_procurement": "complementing",
    "solutions_system_integration": "complementing",
    "customization_and_r&d_services": "complementing",
    "digital_and_streaming_services": "complementing",
    "leasing_and_rental": "substituting",
    "performance_based_contracts": "substituting",
    "recycling_and_process_management": "substituting",
}
