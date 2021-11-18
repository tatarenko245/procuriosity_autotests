create_fa_ful_data_model_ms = {
	"ocid": "ocds-t1s2t3-MD-1637229846659",
	"compiledRelease": {
		"ocid": "ocds-t1s2t3-MD-1637229846659",
		"id": "ocds-t1s2t3-MD-1637229846659-1637229846678",
		"date": "2021-11-18T10:04:06Z",
		"tag": ["compiled"],
		"language": "ro",
		"initiationType": "tender",
		"tender": {
			"id": "3cc70d52-d4f6-4897-9512-3b4ea3a9aa4c",
			"title": "tender.title AP",
			"description": "tender description AP",
			"status": "planning",
			"statusDetails": "aggregatePlanning",
			"value": {
				"currency": "EUR"
			},
			"procurementMethod": "selective",
			"procurementMethodDetails": "testClosedFA",
			"procurementMethodRationale": "tender/procurementMethodRationale AP",
			"hasEnquiries": false,
			"eligibilityCriteria": "Regulile generale privind naționalitatea și originea, precum și alte criterii de eligibilitate sunt enumerate în Ghidul practic privind procedurile de contractare a acțiunilor externe ale UE (PRAG)",
			"contractPeriod": {
				"startDate": "2021-12-10T09:30:00Z",
				"endDate": "2021-12-11T10:30:00Z"
			},
			"acceleratedProcedure": {
				"isAcceleratedProcedure": false
			},
			"classification": {
				"scheme": "CPV",
				"id": "50100000-6",
				"description": "Servicii de reparare şi de întreţinere a vehiculelor şi a echipamentelor aferente şi servicii conexe"
			},
			"designContest": {
				"serviceContractAward": false
			},
			"electronicWorkflows": {
				"useOrdering": false,
				"usePayment": false,
				"acceptInvoicing": false
			},
			"jointProcurement": {
				"isJointProcurement": false
			},
			"legalBasis": "DIRECTIVE_2009_81_EC",
			"procedureOutsourcing": {
				"procedureOutsourced": false
			},
			"dynamicPurchasingSystem": {
				"hasDynamicPurchasingSystem": false
			},
			"framework": {
				"isAFramework": true
			}
		},
		"relatedProcesses": [{
			"id": "ddc62360-4856-11ec-b310-c7ecf598564f",
			"relationship": ["aggregatePlanning"],
			"scheme": "ocid",
			"identifier": "ocds-t1s2t3-MD-1637229846659-AP-1637229846659",
			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637229846659/ocds-t1s2t3-MD-1637229846659-AP-1637229846659"
		}]
	}
}

create_fa_full_data_model_ap = {
	"ocid": "ocds-t1s2t3-MD-1637229846659-AP-1637229846659",
	"compiledRelease": {
		"ocid": "ocds-t1s2t3-MD-1637229846659-AP-1637229846659",
		"id": "ocds-t1s2t3-MD-1637229846659-AP-1637229846659-1637229846678",
		"date": "2021-11-18T10:04:06Z",
		"tag": ["planning"],
		"language": "ro",
		"initiationType": "tender",
		"parties": [{
			"id": "MD-IDNO-3",
			"name": "name of PE from AP (future cpb)",
			"identifier": {
				"scheme": "MD-IDNO",
				"id": "3",
				"legalName": "identifier/legal name",
				"uri": "ident uri"
			},
			"address": {
				"streetAddress": "street address",
				"postalCode": "11",
				"addressDetails": {
					"country": {
						"scheme": "iso-alpha2",
						"id": "MD",
						"description": "Moldova, Republica",
						"uri": "https://www.iso.org"
					},
					"region": {
						"scheme": "CUATM",
						"id": "0101000",
						"description": "mun.Chişinău",
						"uri": "http://statistica.md"
					},
					"locality": {
						"scheme": "other",
						"id": "localityid",
						"description": "locality/description"
					}
				}
			},
			"additionalIdentifiers": [{
				"scheme": "md-idno",
				"id": "445521",
				"legalName": "legalName",
				"uri": "uri"
			}],
			"contactPoint": {
				"name": "contactPoint/name",
				"email": "contactPoint/email",
				"telephone": "contactPoint/456-95-96",
				"faxNumber": "fax-number",
				"url": "CP url"
			},
			"roles": ["centralPurchasingBody"]
		}],
		"tender": {
			"id": "3cc70d52-d4f6-4897-9512-3b4ea3a9aa4c",
			"title": "tender.title AP",
			"description": "tender description AP",
			"status": "planning",
			"statusDetails": "aggregation",
			"tenderPeriod": {
				"startDate": "2020-12-01T11:07:00Z"
			},
			"hasEnquiries": false,
			"documents": [{
				"id": "92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
				"documentType": "evaluationCriteria",
				"title": "document title",
				"description": "document description",
				"url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
				"datePublished": "2021-09-30T11:54:20Z"
			}],
			"submissionMethod": ["electronicSubmission"],
			"submissionMethodDetails": "Lista platformelor: achizitii, ebs, licitatie, yptender",
			"submissionMethodRationale": ["Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice"],
			"requiresElectronicCatalogue": false,
			"procurementMethodRationale": "tender/procurementMethodRationale AP",
			"classification": {
				"scheme": "CPV",
				"id": "50100000-6",
				"description": "Servicii de reparare şi de întreţinere a vehiculelor şi a echipamentelor aferente şi servicii conexe"
			},
			"value": {
				"currency": "EUR"
			}
		},
		"hasPreviousNotice": false,
		"purposeOfNotice": {
			"isACallForCompetition": false
		},
		"relatedProcesses": [{
			"id": "ddc62361-4856-11ec-b310-c7ecf598564f",
			"relationship": ["parent"],
			"scheme": "ocid",
			"identifier": "ocds-t1s2t3-MD-1637229846659",
			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637229846659/ocds-t1s2t3-MD-1637229846659"
		}]
	}
}