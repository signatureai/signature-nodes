# Clearml Nodes

## ReportScore

Reports scores to ClearML.

### Inputs

| Group    | Name  | Type           | Default | Extras |
| -------- | ----- | -------------- | ------- | ------ |
| required | task  | `CLEARML_TASK` |         |        |
| required | score | `FLOAT`        |         |        |
| required | name  | `STRING`       |         |        |
| optional | data  | `any_type`     |         |        |

### Returns

| Name         | Type           |
| ------------ | -------------- |
| clearml_task | `CLEARML_TASK` |

??? note "Source code"

    ```python
    class ReportScore:
        """Reports scores to ClearML."""

        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "task": ("CLEARML_TASK", {}),
                    "score": ("FLOAT",),
                    "name": ("STRING",),
                },
                "optional": {
                    "data": (any_type,),
                },
            }

        RETURN_TYPES = ("CLEARML_TASK",)
        RETURN_NAMES = ("clearml_task",)
        FUNCTION = "process"
        CATEGORY = CLEARML_CAT
        OUTPUT_NODE = True

        def process(self, **kwargs):
            task: Optional[Task] = kwargs.get("task")
            score: Optional[float] = kwargs.get("score")
            name: Optional[str] = kwargs.get("name")
            data: Optional[Any] = kwargs.get("data")

            if task is None or score is None or name is None:
                raise ValueError("Task, score, and name are required")

            task.get_logger().report_single_value(name, score)

            if data is not None:
                df = pd.DataFrame(data)
                task.register_artifact("data", df)

            return (task,)

    ```
