from clearml import Task

from ...categories import CLEARML_CAT


class EndClearmlTask:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "task": ("CLEARML_TASK", {}),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "process"
    CATEGORY = CLEARML_CAT
    OUTPUT_NODE = True

    def process(self, task: Task):
        task.close()
        return ()
