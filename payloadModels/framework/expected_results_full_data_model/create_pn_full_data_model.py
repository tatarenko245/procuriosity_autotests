create_pn_full_data_model_ms = {
  	"ocid": "ocds-t1s2t3-MD-1637228317635",
  	"compiledRelease": {
  		"ocid": "ocds-t1s2t3-MD-1637228317635",
  		"id": "ocds-t1s2t3-MD-1637228317635-1637228317656",
  		"date": "2021-11-18T09:38:37Z",
  		"tag": ["compiled"],
  		"language": "ro",
  		"initiationType": "tender",
  		"planning": {
  			"budget": {
  				"description": "budgetBreakdown description",
  				"amount": {
  					"amount": 90.00,
  					"currency": "EUR"
  				},
  				"isEuropeanUnionFunded": false,
  				"budgetBreakdown": [{
  					"id": "fs-id",
  					"description": "description",
  					"amount": {
  						"amount": 90.00,
  						"currency": "EUR"
  					},
  					"period": {
  						"startDate": "2020-02-01T11:07:00Z",
  						"endDate": "2021-12-31T00:00:00Z"
  					},
  					"sourceParty": {
  						"id": "MD-IDNO-12222",
  						"name": "funder's name"
  					}
  				}]
  			},
  			"rationale": "reason for budget"
  		},
  		"tender": {
  			"id": "082c92ea-3a01-459c-bebb-034e77fc7e70",
  			"title": "platform:tender.title",
  			"description": "platform:tender.description",
  			"status": "planning",
  			"statusDetails": "planning notice",
  			"value": {
  				"amount": 90.00,
  				"currency": "EUR"
  			},
  			"procurementMethod": "selective",
  			"procurementMethodDetails": "directCallOff//requestForQuotations//miniCompetition",
  			"procurementMethodRationale": "tender/procurementMethodRationale",
  			"mainProcurementCategory": "services",
  			"hasEnquiries": false,
  			"eligibilityCriteria": "Regulile generale privind naționalitatea și originea, precum și alte criterii de eligibilitate sunt enumerate în Ghidul practic privind procedurile de contractare a acțiunilor externe ale UE (PRAG)",
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
  			"legalBasis": "NATIONAL_PROCUREMENT_LAW",
  			"procedureOutsourcing": {
  				"procedureOutsourced": false
  			},
  			"procurementMethodAdditionalInfo": "tender/procurementMethodAdditionalInfo",
  			"dynamicPurchasingSystem": {
  				"hasDynamicPurchasingSystem": false
  			},
  			"framework": {
  				"isAFramework": false
  			}
  		},
  		"parties": [{
  			"id": "MD-IDNO-1",
  			"name": "Buyer name",
  			"identifier": {
  				"scheme": "MD-IDNO",
  				"id": "1",
  				"legalName": "legal_name",
  				"uri": "uri"
  			},
  			"address": {
  				"streetAddress": "street address",
  				"postalCode": "postalCode",
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
  						"scheme": "CUATM",
  						"id": "0101000",
  						"description": "mun.Chişinău",
  						"uri": "http://statistica.md"
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
  				"url": "url"
  			},
  			"details": {
  				"typeOfBuyer": "MINISTRY",
  				"mainGeneralActivity": "HEALTH",
  				"mainSectoralActivity": "WATER"
  			},
  			"roles": ["buyer"]
  		}, {
  			"id": "MD-IDNO-111",
  			"name": "Payer's Name1",
  			"identifier": {
  				"scheme": "MD-IDNO",
  				"id": "111",
  				"legalName": "Legal Name",
  				"uri": "http://454.to"
  			},
  			"address": {
  				"streetAddress": "street",
  				"postalCode": "785412",
  				"addressDetails": {
  					"country": {
  						"scheme": "iso-alpha2",
  						"id": "MD",
  						"description": "Moldova, Republica",
  						"uri": "https://www.iso.org"
  					},
  					"region": {
  						"scheme": "CUATM",
  						"id": "3400000",
  						"description": "Donduşeni",
  						"uri": "http://statistica.md"
  					},
  					"locality": {
  						"scheme": "CUATM",
  						"id": "3401000",
  						"description": "or.Donduşeni (r-l Donduşeni)",
  						"uri": "http://statistica.md"
  					}
  				}
  			},
  			"additionalIdentifiers": [{
  				"scheme": "MD-K",
  				"id": "additional identifier",
  				"legalName": "legalname",
  				"uri": "http://k.to"
  			}],
  			"contactPoint": {
  				"name": "contact person",
  				"email": "string@mail.ccc",
  				"telephone": "98-79-87",
  				"faxNumber": "78-56-55",
  				"url": "http://url.com"
  			},
  			"roles": ["payer"]
  		}, {
  			"id": "MD-IDNO-12222",
  			"name": "funder's name1",
  			"identifier": {
  				"scheme": "MD-IDNO",
  				"id": "12222",
  				"legalName": "legal Name",
  				"uri": "http://buyer.com"
  			},
  			"address": {
  				"streetAddress": "street address of buyer",
  				"postalCode": "02054",
  				"addressDetails": {
  					"country": {
  						"scheme": "iso-alpha2",
  						"id": "MD",
  						"description": "Moldova, Republica",
  						"uri": "https://www.iso.org"
  					},
  					"region": {
  						"scheme": "CUATM",
  						"id": "1700000",
  						"description": "Cahul",
  						"uri": "http://statistica.md"
  					},
  					"locality": {
  						"scheme": "CUATM",
  						"id": "1701000",
  						"description": "mun.Cahul",
  						"uri": "http://statistica.md"
  					}
  				}
  			},
  			"additionalIdentifiers": [{
  				"scheme": "scheme",
  				"id": "additional identifier",
  				"legalName": "legal name",
  				"uri": "http://addtIdent.com"
  			}],
  			"contactPoint": {
  				"name": "contact point of buyer",
  				"email": "email.com",
  				"telephone": "32-22-23",
  				"faxNumber": "12-22-21",
  				"url": "http://url.com"
  			},
  			"roles": ["funder"]
  		}],
  		"relatedProcesses": [{
  			"id": "4e67e580-4853-11ec-b310-c7ecf598564f",
  			"relationship": ["planning"],
  			"scheme": "ocid",
  			"identifier": "ocds-t1s2t3-MD-1637228317635-PN-1637228317635",
  			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637228317635/ocds-t1s2t3-MD-1637228317635-PN-1637228317635"
  		}, {
  			"id": "4e67e581-4853-11ec-b310-c7ecf598564f",
  			"relationship": ["x_expenditureItem"],
  			"scheme": "ocid",
  			"identifier": "ocds-t1s2t3-MD-1637080602002",
  			"uri": "http://dev.public.eprocurement.systems/budgets/ocds-t1s2t3-MD-1637080602002/ocds-t1s2t3-MD-1637080602002"
  		}, {
  			"id": "4e67e582-4853-11ec-b310-c7ecf598564f",
  			"relationship": ["x_fundingSource"],
  			"scheme": "ocid",
  			"identifier": "ocds-t1s2t3-MD-1637080602002-FS-1637080716430",
  			"uri": "http://dev.public.eprocurement.systems/budgets/ocds-t1s2t3-MD-1637080602002/ocds-t1s2t3-MD-1637080602002-FS-1637080716430"
  		}]
  	}
  }

