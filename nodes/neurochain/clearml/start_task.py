from clearml import Task

from ...categories import CLEARML_CAT


class StartClearmlTask:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "project_name": ("STRING", {"default": ""}),
                "task_name": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("CLEARML_TASK",)
    RETURN_NAMES = ("clearml_task",)
    FUNCTION = "process"
    CATEGORY = CLEARML_CAT
    OUTPUT_NODE = True

    def process(self, project_name: str, task_name: str):
        task = Task.init(project_name=project_name, task_name=task_name)
        task.get_logger().set_default_upload_destination("s3://signature-ml-models-development/clearml/images/")
        return (task,)
