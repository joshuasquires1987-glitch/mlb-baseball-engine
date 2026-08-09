VALID_PROCESS={"A","B","C","D","E","F"}
VALID_PREDICTION={"A","B","C","D","E","F"}

def build_retrospective(process_grade,prediction_grade,variance_rating,
                        model_error=False,missing_information=False,
                        market_superiority=False,normal_variance=False,
                        notes=""):
    if process_grade not in VALID_PROCESS or prediction_grade not in VALID_PREDICTION:
        raise ValueError("Grades must be A-F")
    if int(variance_rating) not in range(1,6):
        raise ValueError("Variance rating must be 1-5")
    return {
        "process_grade":process_grade,
        "prediction_grade":prediction_grade,
        "variance_rating":int(variance_rating),
        "classifications":{
            "model_error":bool(model_error),
            "missing_information":bool(missing_information),
            "market_superiority":bool(market_superiority),
            "normal_variance":bool(normal_variance),
        },
        "notes":notes,
        "model_mutation_allowed":False,
    }
