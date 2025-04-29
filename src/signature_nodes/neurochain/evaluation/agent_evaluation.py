from neurochain.agents.agent import Agent
from neurochain.evaluation.agent_evaluation import (
    AgentEvaluation as AgentEvaluationNeurochain,
)
from neurochain.evaluation.entities import BaseEvaluation

from ...categories import EVALUATION_CAT


class AgentEvaluation:
    """
    Evaluate a list of agents with a list of evaluators. You need to send a list of prompts and expected outputs.
    Optionally, the results can be reported to ClearML with a project name and task name. The node will return a list of
    scores and a summary of the scores.

    Args:
        agents (list[Agent]): The list of agents to evaluate.
        evaluators (list[BaseEvaluation]): The list of evaluators to use.
        prompts (list[str]): The list of prompts to use for the agents.
        expected_output (list[str]): The list of expected outputs.
        report_to_clearml (bool): Whether to report the results to ClearML.
        project_name (str): The name of the project to report to ClearML.
        task_name (str): The name of the task to report to ClearML.

    Returns:
        tuple: Contains two elements:
            scores (list[dict]): The list of scores.
            scores_summary (dict): The summary of the scores, a row for each agent and a column for each evaluator with
                the average score in the cells.

    Raises:
        ValueError: If the agents, evaluators, prompts, or expected output lists are empty.
        ValueError: If the prompts and expected output lists have different lengths.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "agents": ("LIST", {}),
                "evaluators": ("LIST", {}),
                "prompts": ("LIST", {}),
                "expected_output": ("LIST", {}),
                "report_to_clearml": ("BOOLEAN", {"default": False}),
                "project_name": ("STRING", {"default": "Agent Evaluation"}),
                "task_name": ("STRING", {"default": "Agent Evaluation Task"}),
            }
        }

    RETURN_TYPES = ("LIST", "DICT")
    RETURN_NAMES = ("scores", "scores_summary")
    FUNCTION = "process"
    CATEGORY = EVALUATION_CAT
    OUTPUT_NODE = True

    def process(
        self,
        agents: list[Agent],
        evaluators: list[BaseEvaluation],
        prompts: list[str],
        expected_output: list[str],
        report_to_clearml: bool,
        project_name: str,
        task_name: str,
    ):
        if agents is None or len(agents) == 0:
            raise ValueError("Agents list cannot be empty")
        if evaluators is None or len(evaluators) == 0:
            raise ValueError("Evaluators list cannot be empty")
        if prompts is None or len(prompts) == 0:
            raise ValueError("Prompts list cannot be empty")
        if expected_output is None or len(expected_output) == 0:
            raise ValueError("Expected output list cannot be empty")
        if len(prompts) != len(expected_output):
            raise ValueError("Prompts and expected output lists must have the same length")

        agent_evaluation = AgentEvaluationNeurochain(agents, evaluators, project_name, task_name)
        scores = agent_evaluation.evaluate(prompts, expected_output, report_to_clearml)
        scores_summary = agent_evaluation.scores_summary(scores)
        return (scores, scores_summary)
