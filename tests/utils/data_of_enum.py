typeOfBuyer = ("BODY_PUBLIC", "EU_INSTITUTION", "MINISTRY", "NATIONAL_AGENCY", "REGIONAL_AGENCY", "REGIONAL_AUTHORITY",)
mainGeneralActivity = (
    "DEFENCE", "ECONOMIC_AND_FINANCIAL_AFFAIRS", "EDUCATION", "ENVIRONMENT", "GENERAL_PUBLIC_SERVICES", "HEALTH",
    "HOUSING_AND_COMMUNITY_AMENITIES", "PUBLIC_ORDER_AND_SAFETY", "RECREATION_CULTURE_AND_RELIGION",
    "SOCIAL_PROTECTION",)
mainSectoralActivity = ("AIRPORT_RELATED_ACTIVITIES", "ELECTRICITY", "EXPLORATION_EXTRACTION_COAL_OTHER_SOLID_FUEL",
                        "EXPLORATION_EXTRACTION_GAS_OIL",
                        "PORT_RELATED_ACTIVITIES", "POSTAL_SERVICES", "PRODUCTION_TRANSPORT_DISTRIBUTION_GAS_HEAT",
                        "RAILWAY_SERVICES", "URBAN_RAILWAY_TRAMWAY_TROLLEYBUS_BUS_SERVICES", "WATER",)
unit_id = ("10", "18", "19", "20", "21",)
cpvs = ("AA01-1", "AA02-4", "AA05-3", "AA07-9","AA14-0",)
cpv_category = ("goods", "works", "services",)
cpv_goods_high_level = ("03100000-2", "14600000-7", "22100000-1", "30100000-0", "44400000-4", "48200000-0",)
cpv_works_high_level = ("45100000-8",)
cpv_services_high_level = ("51500000-7", "63700000-6", "71300000-1", "85100000-0", "92300000-4", "98300000-6",)

cpv_goods_low_level_03 = ("03112000-9", "03115100-1", "03142100-9", "03144000-2", "03111800-0", "03111900-1",)
cpv_goods_low_level_1 = ("14612300-7", "14612400-8", "14630000-6", "14613100-2", "14621110-4", "14621120-7",)
cpv_goods_low_level_2 = ("22121000-4", "22130000-0", "22140000-3", "22150000-6", "22160000-9", "22114500-7",)
cpv_goods_low_level_3 = ("30124130-4", "30124140-7", "30124150-0", "30124200-6", "30124300-7", "30124400-8",)
cpv_goods_low_level_44 = ("44411710-4", "44411720-7", "44411740-3", "44411750-6", "44411800-2", "44411700-1",)
cpv_goods_low_level_48 = ("48217100-3", "48217200-4", "48217300-5", "48218000-9", "48219000-6", "48219100-7",)
cpv_works_low_level_45 = ("45112350-3", "45112360-6", "45112400-9", "45112410-2", "45112420-5", "45112440-1",)
cpv_services_low_level_5 = ("51543400-4", "51544000-7", "51544100-8", "51544200-9", "51545000-4", "51550000-2",)
cpv_services_low_level_6 = ("63712311-6", "63712320-2", "63712321-9", "63712400-7", "63712500-8", "63712600-9",)
cpv_services_low_level_7 = ("71313450-4", "71314000-2", "71314100-3", "71314200-4", "71314300-5", "71314310-8",)
cpv_services_low_level_8 = ("85111310-6", "85111320-9", "85111400-4", "85111500-5", "85111600-6", "85111700-7",)
cpv_services_low_level_92 = ("92312220-9", "92312230-2", "92312240-5", "92312250-8", "92312251-5", "92320000-0",)
cpv_services_low_level_98 = ("98341110-9", "98341120-2", "98341130-5", "98341140-8", "98342000-2", "98351000-8",)

cpv_works_low_level = ()
cpv_service_low_level = ()
region_id = ("1700000", "2500000", "2900000", "3400000", "4800000",)
locality_id =("1701000","2501000", "2901000", "3401000", "4801000",)
locality_scheme = ("CUATM", "other",)

currency = ("USD", "EUR", "MDL",)

legalBasis = ("DIRECTIVE_2014_23_EU", "DIRECTIVE_2014_24_EU", "DIRECTIVE_2014_25_EU", "DIRECTIVE_2009_81_EC",
              "REGULATION_966_2012", "NATIONAL_PROCUREMENT_LAW",)

documentType = ("tenderNotice",
                "biddingDocuments",
                "technicalSpecifications",
                "evaluationCriteria",
                "clarifications",
                "eligibilityCriteria",
                "riskProvisions",
                "billOfQuantity",
                "conflictOfInterest",
                "procurementPlan",
                "contractDraft",
                "complaints",
                "illustration",
                "cancellationDetails",
                "evaluationReports",
                "shortlistedFirms",
                "contractArrangements",
                "contractGuarantees",)

documentType_for_create_award_of_limited_procedure = (
    "awardNotice",
    "evaluationReports",
    "contractDraft",
    "winningBid",
    "complaints",
    "bidders",
    "conflictOfInterest",
    "cancellationDetails",
    "submissionDocuments",
    "contractArrangements",
    "contractSchedule",
    "shortlistedFirms",)

scale = ("micro",
         "sme",
         "large",)

documentType_for_bid = (
    "illustration",
    "submissionDocuments",
    "x_qualificationDocuments",
    "x_eligibilityDocuments",
    "x_technicalDocuments",)

documentType_for_evaluate_award = (
    "awardNotice",
    "evaluationReports",
    "contractDraft",
    "winningBid",
    "complaints",
    "bidders",
    "conflictOfInterest",
    "cancellationDetails",
    "submissionDocuments",
    "contractArrangements",
    "contractSchedule",
    "shortlistedFirms",)

person_title = ("Mr.", "Ms.", "Mrs.",)
business_function_type = ("authority", "contactPoint",)
business_function_type_for_declare = (
    "chairman",
    "procurementOfficer",
    "contactPoint",
    "technicalEvaluator",
    "technicalOpener",
    "priceOpener",
    "priceEvaluator",
)
type_of_supplier = ("company", "individual",)
