from rc2_context_calibration import log_loss,brier
def test_metrics_improve_for_good_probabilities():
 assert log_loss([1,0],[.9,.1]) < log_loss([1,0],[.5,.5])
 assert brier([1,0],[.9,.1]) < brier([1,0],[.5,.5])
