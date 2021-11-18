  create_fe_full_data_model_without_auction_ms = {
 	"ocid": "ocds-t1s2t3-MD-1637238092279",
 	"compiledRelease": {
 		"ocid": "ocds-t1s2t3-MD-1637238092279",
 		"id": "ocds-t1s2t3-MD-1637238092279-AP-1637238092279-1637238114409",
 		"date": "2021-11-18T12:21:54Z",
 		"tag": ["compiled"],
 		"language": "ro",
 		"initiationType": "tender",
 		"tender": {
 			"id": "e035646e-dba2-4bc9-a293-fcddca136d8f",
 			"title": "createFE:tender.title",
 			"description": "createFE:tender.description",
 			"status": "active",
 			"statusDetails": "establishment",
 			"value": {
 				"amount": 12.00,
 				"currency": "EUR"
 			},
 			"procurementMethod": "selective",
 			"procurementMethodDetails": "testClosedFA",
 			"procurementMethodRationale": "createFE:procurementMethodRationale",
 			"mainProcurementCategory": "services",
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
 			"id": "108be6a0-486a-11ec-b310-c7ecf598564f",
 			"relationship": ["aggregatePlanning"],
 			"scheme": "ocid",
 			"identifier": "ocds-t1s2t3-MD-1637238092279-AP-1637238092279",
 			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637238092279/ocds-t1s2t3-MD-1637238092279-AP-1637238092279"
 		}, {
 			"id": "f0184e96-9e96-419e-9f16-3d1a0e51acbe",
 			"relationship": ["x_demand"],
 			"scheme": "ocid",
 			"identifier": "ocds-t1s2t3-MD-1637238043904",
 			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637238043904/ocds-t1s2t3-MD-1637238043904"
 		}, {
 			"id": "1db9c590-486a-11ec-b310-c7ecf598564f",
 			"relationship": ["x_establishment"],
 			"scheme": "ocid",
 			"identifier": "ocds-t1s2t3-MD-1637238092279-FE-1637238114342",
 			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637238092279/ocds-t1s2t3-MD-1637238092279-FE-1637238114342"
 		}]
 	}
 }

  create_fe_full_data_model_without_auction_ap = {
 	"ocid": "ocds-t1s2t3-MD-1637238092279-AP-1637238092279",
 	"compiledRelease": {
 		"ocid": "ocds-t1s2t3-MD-1637238092279-AP-1637238092279",
 		"id": "ocds-t1s2t3-MD-1637238092279-AP-1637238092279-1637238114409",
 		"date": "2021-11-18T12:21:54Z",
 		"tag": ["planningUpdate"],
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
 		}, {
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
 			"roles": ["client"]
 		}],
 		"tender": {
 			"id": "cdb9d233-a306-431a-ac75-8981dabba487",
 			"title": "tender.title AP",
 			"description": "tender description AP",
 			"status": "planned",
 			"statusDetails": "aggregated",
 			"items": [{
 				"id": "714f54dd-3124-4666-9681-396a91be6423",
 				"description": "itemdescription.",
 				"classification": {
 					"scheme": "CPV",
 					"id": "50100000-6",
 					"description": "Servicii de reparare şi de întreţinere a vehiculelor şi a echipamentelor aferente şi servicii conexe"
 				},
 				"quantity": 1.000,
 				"unit": {
 					"name": "Parsec",
 					"id": "10"
 				},
 				"relatedLot": "abba8bcf-b53b-44a2-9112-75fce041d717"
 			}],
 			"lots": [{
 				"id": "abba8bcf-b53b-44a2-9112-75fce041d717",
 				"title": "lots.titleNew",
 				"description": "lots.description",
 				"status": "planning",
 				"statusDetails": "empty",
 				"placeOfPerformance": {
 					"address": {
 						"addressDetails": {
 							"country": {
 								"scheme": "iso-alpha2",
 								"id": "MD",
 								"description": "Moldova, Republica",
 								"uri": "https://www.iso.org"
 							},
 							"region": {
 								"scheme": "CUATM",
 								"id": "1000000",
 								"description": "Anenii Noi",
 								"uri": "http://statistica.md"
 							},
 							"locality": {
 								"scheme": "CUATM",
 								"id": "1001001",
 								"description": "s.Albiniţa",
 								"uri": "http://statistica.md"
 							}
 						}
 					}
 				}
 			}, {
 				"id": "7bb0084d-7dea-448e-b68b-6f6d54c5f03a",
 				"title": "lots.titleNew",
 				"description": "lots.description",
 				"status": "planning",
 				"statusDetails": "empty",
 				"placeOfPerformance": {
 					"address": {
 						"addressDetails": {
 							"country": {
 								"scheme": "iso-alpha2",
 								"id": "MD",
 								"description": "Moldova, Republica",
 								"uri": "https://www.iso.org"
 							},
 							"region": {
 								"scheme": "CUATM",
 								"id": "1000000",
 								"description": "Anenii Noi",
 								"uri": "http://statistica.md"
 							},
 							"locality": {
 								"scheme": "CUATM",
 								"id": "1001001",
 								"description": "s.Albiniţa",
 								"uri": "http://statistica.md"
 							}
 						}
 					}
 				}
 			}],
 			"tenderPeriod": {
 				"startDate": "2020-08-01T11:07:00Z"
 			},
 			"hasEnquiries": false,
 			"documents": [{
 				"id": "92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
 				"documentType": "evaluationCriteria",
 				"title": "doctitle`",
 				"description": "docdesc`",
 				"url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
 				"datePublished": "2021-09-30T11:54:20Z",
 				"relatedLots": ["7bb0084d-7dea-448e-b68b-6f6d54c5f03a"]
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
 				"amount": 12.00,
 				"currency": "EUR"
 			}
 		},
 		"hasPreviousNotice": false,
 		"purposeOfNotice": {
 			"isACallForCompetition": false
 		},
 		"relatedProcesses": [{
 			"id": "108be6a1-486a-11ec-b310-c7ecf598564f",
 			"relationship": ["parent"],
 			"scheme": "ocid",
 			"identifier": "ocds-t1s2t3-MD-1637238092279",
 			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637238092279/ocds-t1s2t3-MD-1637238092279"
 		}, {
 			"id": "b7682100-e42e-45cc-aaf9-8f80d983b7de",
 			"relationship": ["x_scope"],
 			"scheme": "ocid",
 			"identifier": "ocds-t1s2t3-MD-1637238043904-PN-1637238043904",
 			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637238043904/ocds-t1s2t3-MD-1637238043904-PN-1637238043904"
 		}]
 	}
 }

   create_fe_full_data_model_without_auction_fe = {
  	"ocid": "ocds-t1s2t3-MD-1637238092279-FE-1637238114342",
  	"compiledRelease": {
  		"ocid": "ocds-t1s2t3-MD-1637238092279-FE-1637238114342",
  		"id": "ocds-t1s2t3-MD-1637238092279-FE-1637238114342-1637238114408",
  		"date": "2021-11-18T12:21:54Z",
  		"tag": ["tender"],
  		"initiationType": "tender",
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
  			"persones": [{
  				"id": "MD-IDNO-84",
  				"title": "Mr.",
  				"name": "Person from FE",
  				"identifier": {
  					"scheme": "MD-IDNO",
  					"id": "84",
  					"uri": "uri"
  				},
  				"businessFunctions": [{
  					"id": "businessFunctions1",
  					"type": "chairman",
  					"jobTitle": "string",
  					"period": {
  						"startDate": "2020-09-22T14:38:20Z"
  					},
  					"documents": [{
  						"id": "92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
  						"documentType": "regulatoryDocument",
  						"title": "string",
  						"description": "string"
  					}]
  				}]
  			}],
  			"roles": ["procuringEntity"]
  		}],
  		"tender": {
  			"id": "e035646e-dba2-4bc9-a293-fcddca136d8f",
  			"title": "createFE:tender.title",
  			"description": "createFE:tender.description",
  			"status": "active",
  			"statusDetails": "submission",
  			"criteria": [{
  				"id": "b31044d8-9200-4a4b-8ade-35534d067c6c",
  				"title": "criteria for tenderer1",
  				"source": "tenderer",
  				"description": "criteria description",
  				"requirementGroups": [{
  					"id": "b7099e67-c283-4dce-8619-5cb51e2c7017",
  					"description": "RG1 for lot",
  					"requirements": [{
  						"id": "ec51c7b9-31ab-44e5-b7e1-78b110ff09c3",
  						"title": "Your age???",
  						"dataType": "number",
  						"status": "active",
  						"datePublished": "2021-11-18T12:21:54Z",
  						"description": "sdrg",
  						"period": {
  							"startDate": "2021-12-26T14:45:00Z",
  							"endDate": "2021-12-30T14:45:00Z"
  						},
  						"eligibleEvidences": [{
  							"id": "35",
  							"title": "2",
  							"type": "document",
  							"description": "3"
  						}],
  						"expectedValue": 4.000
  					}]
  				}],
  				"relatesTo": "tenderer",
  				"classification": {
  					"scheme": "ESPD-2.2.1",
  					"id": "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION"
  				}
  			}, {
  				"id": "aab0f3ca-6285-491f-894c-6249cd73c4e1",
  				"title": "criteria for tenderer2",
  				"source": "tenderer",
  				"description": "criteria description",
  				"requirementGroups": [{
  					"id": "4172c5c2-04c8-4b67-a153-6d7aefe04efa",
  					"description": "RG1 for lot",
  					"requirements": [{
  						"id": "8a8ddc05-e588-4afa-bce3-2b98f1d98665",
  						"title": "Your age???",
  						"dataType": "number",
  						"status": "active",
  						"datePublished": "2021-11-18T12:21:54Z",
  						"description": "sdrg",
  						"period": {
  							"startDate": "2021-12-26T14:45:00Z",
  							"endDate": "2021-12-30T14:45:00Z"
  						},
  						"eligibleEvidences": [{
  							"id": "85557",
  							"title": "2",
  							"type": "document",
  							"description": "3"
  						}, {
  							"id": "88",
  							"title": "string",
  							"type": "document",
  							"description": "string",
  							"relatedDocument": {
  								"id": "92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899"
  							}
  						}],
  						"minValue": 2.500,
  						"maxValue": 3.300
  					}]
  				}],
  				"relatesTo": "tenderer",
  				"classification": {
  					"scheme": "ESPD-2.2.1",
  					"id": "CRITERION.EXCLUSION.SOCIAL.SOCIAL_LAW"
  				}
  			}, {
  				"id": "17e6f291-6eca-4dd6-b4b0-52171663aaad",
  				"title": "criteria for tenderer2",
  				"source": "tenderer",
  				"description": "criteria description",
  				"requirementGroups": [{
  					"id": "c4464668-7539-4e6d-972e-f36d4fcf7f52",
  					"description": "RG1 for lot",
  					"requirements": [{
  						"id": "fd2ae744-12da-40c6-bcbe-2533f8d72943",
  						"title": "Your age???",
  						"dataType": "number",
  						"status": "active",
  						"datePublished": "2021-11-18T12:21:54Z",
  						"description": "sdrg",
  						"period": {
  							"startDate": "2021-12-26T14:45:00Z",
  							"endDate": "2021-12-30T14:45:00Z"
  						},
  						"eligibleEvidences": [{
  							"id": "07",
  							"title": "2",
  							"type": "document",
  							"description": "3"
  						}, {
  							"id": "08",
  							"title": "string",
  							"type": "document"
  						}],
  						"minValue": 2.500,
  						"maxValue": 3.300
  					}]
  				}],
  				"relatesTo": "tenderer",
  				"classification": {
  					"scheme": "ESPD-2.2.1",
  					"id": "CRITERION.EXCLUSION.SOCIAL.LABOUR_LAW"
  				}
  			}, {
  				"id": "98ca734e-1318-4563-abb5-af9c644ca3eb",
  				"title": "criteria for tenderer2",
  				"source": "tenderer",
  				"description": "criteria description",
  				"requirementGroups": [{
  					"id": "72ed939f-0225-48f1-80c7-350ba57b86c4",
  					"description": "RG1 for lot",
  					"requirements": [{
  						"id": "5906519a-60ca-4a1f-8a1d-ed7a78c4c838",
  						"title": "Your age???",
  						"dataType": "number",
  						"status": "active",
  						"datePublished": "2021-11-18T12:21:54Z",
  						"description": "sdrg",
  						"period": {
  							"startDate": "2021-12-26T14:45:00Z",
  							"endDate": "2021-12-30T14:45:00Z"
  						},
  						"eligibleEvidences": [{
  							"id": "7555",
  							"title": "2",
  							"type": "document",
  							"description": "3"
  						}, {
  							"id": "55558",
  							"title": "string",
  							"type": "document"
  						}],
  						"minValue": 2.500,
  						"maxValue": 3.300
  					}]
  				}],
  				"relatesTo": "tenderer",
  				"classification": {
  					"scheme": "ESPD-2.2.1",
  					"id": "CRITERION.SELECTION.TECHNICAL_PROFESSIONAL_ABILITY.CERTIFICATES.ENVIRONMENTAL_MANAGEMENT.ENV_INDEPENDENT_CERTIFICATE"
  				}
  			}],
  			"otherCriteria": {
  				"reductionCriteria": "none",
  				"qualificationSystemMethods": ["manual"]
  			},
  			"enquiryPeriod": {
  				"startDate": "2021-11-18T12:21:54Z",
  				"endDate": "2021-12-03T12:42:00Z"
  			},
  			"hasEnquiries": false,
  			"documents": [{
  				"id": "92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
  				"documentType": "evaluationCriteria",
  				"title": "doctitle`",
  				"description": "docdesc`",
  				"url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/92f6d26c-cd55-4192-9a2a-798d934c6fc9-1633002324899",
  				"datePublished": "2021-09-30T11:54:20Z"
  			}],
  			"submissionMethod": ["electronicSubmission"],
  			"submissionMethodDetails": "Lista platformelor: achizitii, ebs, licitatie, yptender",
  			"submissionMethodRationale": ["Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice"],
  			"requiresElectronicCatalogue": false,
  			"secondStage": {
  				"minimumCandidates": 1,
  				"maximumCandidates": 3
  			},
  			"procurementMethodRationale": "createFE:procurementMethodRationale",
  			"classification": {
  				"scheme": "CPV",
  				"id": "50100000-6",
  				"description": "Servicii de reparare şi de întreţinere a vehiculelor şi a echipamentelor aferente şi servicii conexe"
  			},
  			"value": {
  				"amount": 12.00,
  				"currency": "EUR"
  			},
  			"procuringEntity": {
  				"id": "MD-IDNO-3",
  				"name": "name of PE from AP (future cpb)"
  			}
  		},
  		"preQualification": {
  			"period": {
  				"startDate": "2021-11-18T12:21:54Z",
  				"endDate": "2021-12-03T12:43:00Z"
  			}
  		},
  		"hasPreviousNotice": true,
  		"purposeOfNotice": {
  			"isACallForCompetition": true
  		},
  		"relatedProcesses": [{
  			"id": "49c8f062-a5ce-4cde-99fe-aebd4df4224e",
  			"relationship": ["aggregatePlanning"],
  			"scheme": "ocid",
  			"identifier": "ocds-t1s2t3-MD-1637238092279-AP-1637238092279",
  			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637238092279/ocds-t1s2t3-MD-1637238092279-AP-1637238092279"
  		}, {
  			"id": "f443b86a-2fec-4aaf-89fb-6fcea283df2a",
  			"relationship": ["parent"],
  			"scheme": "ocid",
  			"identifier": "ocds-t1s2t3-MD-1637238092279",
  			"uri": "http://dev.public.eprocurement.systems/tenders/ocds-t1s2t3-MD-1637238092279/ocds-t1s2t3-MD-1637238092279"
  		}]
  	}
  }