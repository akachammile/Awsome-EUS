# cython: language_level=3

from ultralytics.engine.model import Model
from ultralytics.nn.tasks import guess_model_task, yaml_model_load
from ultralytics.utils import ROOT,DEFAULT_CFG_DICT,RANK
from ultralytics.models import yolo
from ultralytics.nn.tasks import ClassificationModel, DetectionModel, OBBModel, PoseModel, SegmentationModel

class YOLOV8(Model):
    def __init__(self, task: str = None, verbose: bool = False, nc=1, scale:str="s") -> None:
        model = ROOT / "cfg/models/v8/yolov8.yaml"
        self.nc = nc # 分类
        self.scale = scale #模型特征(n,s,l,m,x)
        super().__init__(model, task, verbose)
        
    def _new(self, cfg: str, task=None, model=None, verbose=False) -> None:
        """
        Initializes a new model and infers the task type from the model definitions.

        This method creates a new model instance based on the provided configuration file. It loads the model
        configuration, infers the task type if not specified, and initializes the model using the appropriate
        class from the task map.

        Args:
            cfg (str): Path to the model configuration file in YAML format.
            task (str | None): The specific task for the model. If None, it will be inferred from the config.
            model (torch.nn.Module | None): A custom model instance. If provided, it will be used instead of creating
                a new one.
            verbose (bool): If True, displays model information during loading.

        Raises:
            ValueError: If the configuration file is invalid or the task cannot be inferred.
            ImportError: If the required dependencies for the specified task are not installed.

        Examples:
            >>> model = Model()
            >>> model._new('yolov8n.yaml', task='detect', verbose=True)
        """
        cfg_dict = yaml_model_load(cfg)
        cfg_dict["nc"] = self.nc #更新分类
        cfg_dict["scale"] = self.scale #更新模型特征(n,s,l,m,x)
        self.cfg = cfg
        self.task = task or guess_model_task(cfg_dict)
        self.model = (model or self._smart_load("model"))(cfg_dict, verbose=verbose and RANK == -1)  # build model
        self.overrides["model"] = self.cfg
        self.overrides["task"] = self.task

        # Below added to allow export from YAMLs
        self.model.args = {**DEFAULT_CFG_DICT, **self.overrides}  # combine default and model args (prefer model args)
        self.model.task = self.task
        self.model_name = cfg
  
    @property
    def task_map(self):
        """Map head to model, trainer, validator, and predictor classes."""
        return {
            "classify": {
                "model": ClassificationModel,
                "trainer": yolo.classify.ClassificationTrainer,
                "validator": yolo.classify.ClassificationValidator,
                "predictor": yolo.classify.ClassificationPredictor,
            },
            "detect": {
                "model": DetectionModel,
                "trainer": yolo.detect.DetectionTrainer,
                "validator": yolo.detect.DetectionValidator,
                "predictor": yolo.detect.DetectionPredictor,
            },
            "segment": {
                "model": SegmentationModel,
                "trainer": yolo.segment.SegmentationTrainer,
                "validator": yolo.segment.SegmentationValidator,
                "predictor": yolo.segment.SegmentationPredictor,
            },
            "pose": {
                "model": PoseModel,
                "trainer": yolo.pose.PoseTrainer,
                "validator": yolo.pose.PoseValidator,
                "predictor": yolo.pose.PosePredictor,
            },
            "obb": {
                "model": OBBModel,
                "trainer": yolo.obb.OBBTrainer,
                "validator": yolo.obb.OBBValidator,
                "predictor": yolo.obb.OBBPredictor,
            },
        }

