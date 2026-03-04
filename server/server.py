import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import flwr as fl
from blockchain import BlockchainLogger

# Initialize blockchain logger
logger = BlockchainLogger()

class FLServer(fl.server.strategy.FedAvg):
    def aggregate_fit(self, server_round, results, failures):
        logger.log("ROUND_FIT_COMPLETE", {
            "round": server_round,
            "num_clients": len(results),
            "num_failures": len(failures)
        })
        return super().aggregate_fit(server_round, results, failures)

    def aggregate_evaluate(self, server_round, results, failures):
        logger.log("ROUND_EVALUATE_COMPLETE", {
            "round": server_round,
            "num_clients": len(results),
            "client_metrics": [
                {
                    "client": i + 1,
                    "recall": r.metrics.get("recall", 0),
                    "precision": r.metrics.get("precision", 0),
                    "f1": r.metrics.get("f1", 0)
                }
                for i, (_, r) in enumerate(results)
            ]
        })
        return super().aggregate_evaluate(server_round, results, failures)


# Your original settings preserved here
strategy = FLServer(
    fraction_fit=1.0,
    fraction_evaluate=1.0,
    min_fit_clients=3,
    min_available_clients=3,
)

logger.log("SERVER_START", {
    "message": "Federated Learning server initialised",
    "min_clients": 3,
    "num_rounds": 3
})

# Start server
fl.server.start_server(
    server_address="localhost:8080",
    config=fl.server.ServerConfig(num_rounds=3),
    strategy=strategy,
)

logger.log("SERVER_END", {"message": "All training rounds completed"})
logger.verify_chain()
logger.print_chain()
logger.save_chain("audit_log.json")


