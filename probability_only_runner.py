from dual_model_runner import DualModelRunner

class ProbabilityOnlyRunner:
    """Runs baseball probabilities with no sportsbook object in scope."""
    def __init__(self,repo_root="."):
        self.runner=DualModelRunner(repo_root)

    def predict(self,model_inputs):
        prod,shadow=self.runner.predict(model_inputs)
        return {
            "production":prod,
            "shadow":shadow,
            "probabilities_frozen":True,
            "prices_seen":False,
        }
