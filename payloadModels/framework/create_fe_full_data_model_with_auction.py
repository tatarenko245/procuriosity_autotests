  create_fe_full_data_model_with_auction = {
	"preQualification": {
		"period": {
			"endDate": "2021-11-03T12:43:00Z"
		}
	},
	"tender": {
		"title": "tender.title",
		"description": "tender.description",
		"secondStage": {
			"minimumCandidates": 1,
			"maximumCandidates": 3
		},
		"procurementMethodModalities": [
			"electronicAuction"
		],

		"procurementMethodRationale": "tender.procurementMethodRationale",
		"procuringEntity": {
			"id": "MD-IDNO-3",
			"persones": [{
				"title": "Mr.",
				"name": "Person from FE",
				"identifier": {
					"scheme": "MD-IDNO",
					"id": "84",
					"uri": "uri"
				},
				"businessFunctions": [{
					"id": "businessFunctions.id",
					"type": "chairman",
					"jobTitle": "string",
					"period": {
						"startDate": "2020-09-22T14:38:20Z"
					},
					"documents": [{
						"id": "{{doc}}",
						"documentType": "regulatoryDocument",
						"title": "string",
						"description": "string"
					}]
				}]
			}]
		},
		"criteria": [{
				"id": "CRITERION.1",
				"title": "criteria for tenderer1",
				"classification": {
					"id": "CRITERION.EXCLUSION.CONVICTIONS.PARTICIPATION_IN_CRIMINAL_ORGANISATION",
					"scheme": "ESPD-2.2.1"
				},

				"relatesTo": "tenderer",
				"description": "criteria description",
				"requirementGroups": [{
					"id": "1",
					"description": "RG1 for lot",
					"requirements": [{
						"id": "2",
						"title": "Your age???",
						"description": "sdrg",
						"dataType": "number",

						"eligibleEvidences": [{
								"id": "35",
								"title": "2",
								"description": "3",
								"type": "document",
								"relatedDocument": {
									"id": ""
								}
							}

						],

						"expectedValue": 4,
						"period": {
							"startDate": "2021-12-26T14:45:00Z",
							"endDate": "2021-12-30T14:45:00Z"
						}
					}]
				}]
			},
			{
				"id": "CRITERION.212",
				"title": "criteria for tenderer2",
				"classification": {
					"id": "CRITERION.EXCLUSION.SOCIAL.SOCIAL_LAW",
					"scheme": "ESPD-2.2.1"
				},

				"relatesTo": "tenderer",
				"description": "criteria description",
				"requirementGroups": [{
					"id": "88865",
					"description": "RG1 for lot",
					"requirements": [{
						"id": "886",
						"title": "Your age???",
						"description": "sdrg",
						"dataType": "number",

						"eligibleEvidences": [{
								"id": "85557",
								"title": "2",
								"description": "3",
								"type": "document",
								".relatedDocument": {
									"id": ""
								}
							},
							{
								"id": "88",
								"title": "string",
								"description": "string",
								"type": "document",
								"relatedDocument": {
									"id": "{{doc}}"
								}
							}
						],
						"minValue": 2.5,
						"maxValue": 3.3,

						"period": {
							"startDate": "2021-12-26T14:45:00Z",
							"endDate": "2021-12-30T14:45:00Z"
						}
					}]
				}]
			},
			{
				"id": "CRITERION.1222",
				"title": "criteria for tenderer2",
				"classification": {
					"id": "CRITERION.EXCLUSION.SOCIAL.LABOUR_LAW",
					"scheme": "ESPD-2.2.1"
				},

				"relatesTo": "tenderer",
				"description": "criteria description",
				"requirementGroups": [{
					"id": "05",
					"description": "RG1 for lot",
					"requirements": [{
						"id": "06",
						"title": "Your age???",
						"description": "sdrg",
						"dataType": "number",

						"eligibleEvidences": [{
								"id": "07",
								"title": "2",
								"description": "3",
								"type": "document",
								"relatedDocument": {
									"id": ""
								}
							},
							{
								"id": "08",
								"title": "string",
								"/description": "string",
								"type": "document",
								"/relatedDocument": {
									"id": "{{doc}}"
								}
							}
						],
						"minValue": 2.5,
						"maxValue": 3.3,
						"/expectedValue": 4,
						"period": {
							"startDate": "2021-12-26T14:45:00Z",
							"endDate": "2021-12-30T14:45:00Z"
						}
					}]
				}]
			},
			{
				"id": "CRITER333ION.1222",
				"title": "criteria for tenderer2",
				"classification": {
					"id": "CRITERION.SELECTION.TECHNICAL_PROFESSIONAL_ABILITY.CERTIFICATES.ENVIRONMENTAL_MANAGEMENT.ENV_INDEPENDENT_CERTIFICATE",
					"scheme": "ESPD-2.2.1"
				},
				"/relatedItem": "{{lot-id-1}}",
				"relatesTo": "tenderer",
				"description": "criteria description",
				"requirementGroups": [{
					"id": "95",
					"description": "RG1 for lot",
					"requirements": [{
						"id": "46",
						"title": "Your age???",
						"description": "sdrg",
						"dataType": "number",
						"/status": "active",
						"/datePublished": "2021-12-26T14:45:00Z",
						"eligibleEvidences": [{
								"id": "7555",
								"title": "2",
								"description": "3",
								"type": "document",
								".relatedDocument": {
									"id": ""
								}
							},
							{
								"id": "55558",
								"title": "string",
								"/description": "string",
								"type": "document",
								"/relatedDocument": {
									"id": "{{doc}}"
								}
							}
						],
						"minValue": 2.5,
						"maxValue": 3.3,

						"period": {
							"startDate": "2021-12-26T14:45:00Z",
							"endDate": "2021-12-30T14:45:00Z"
						}
					}]
				}]
			}
		],

		"otherCriteria": {
			"qualificationSystemMethods": [
				"manual"
			],
			"reductionCriteria": "none"
		},
		"documents": [{
			"documentType": "evaluationCriteria",
			"id": "{{doc}}",
			"title": "doctitle`",
			"description": "docdesc`"

		}]
	}
}