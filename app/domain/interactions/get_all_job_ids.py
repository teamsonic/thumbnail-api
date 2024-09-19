from app.task_queue import broker


def get_all_job_ids() -> list[str]:
    results_dict = broker.get_all_results()
    results: list[str] = []
    for category in results_dict.values():
        results.extend(category)
    return results
